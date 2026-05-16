<?php
/**
 * CAPI Gateway — Plugin Auto-Update
 *
 * আপনার সার্ভার থেকে প্লাগইনের নতুন ভার্সন চেক করে।
 * WordPress Dashboard থেকে ওয়ান-ক্লিকে আপডেট করার সুবিধা দেয়।
 *
 * কাজের ধরন:
 * 1. WordPress যখন প্লাগইন আপডেট চেক করে, আমরা আমাদের সার্ভারে একটি
 *    রিকোয়েস্ট পাঠাই — নতুন ভার্সন আছে কিনা দেখতে।
 * 2. নতুন ভার্সন থাকলে WordPress-এর স্ট্যান্ডার্ড আপডেট নোটিফিকেশন দেখায়।
 * 3. "Update Now" ক্লিক করলে সার্ভার থেকে ZIP ডাউনলোড করে ইন্সটল করে।
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class CAPIGW_Auto_Updater {

    private $plugin_slug;
    private $plugin_file;
    private $current_version;
    private $update_url;

    public function __construct() {
        $this->plugin_slug    = 'capi-gateway';
        $this->plugin_file    = 'capi-gateway/capi-gateway.php';
        $this->current_version = CAPIGW_VERSION;

        // Build update check URL from gateway settings
        $settings = capigw_get_settings();
        $gateway  = rtrim( $settings['gateway_url'], '/' );
        // Remove /api/v1 to get base URL
        $base_url = preg_replace( '#/api/v1/?$#', '', $gateway );
        $this->update_url = $base_url . '/api/v1/plugin/update-check';

        // Hook into WordPress update system
        add_filter( 'pre_set_site_transient_update_plugins', array( $this, 'check_for_update' ) );
        add_filter( 'plugins_api', array( $this, 'plugin_info' ), 20, 3 );
        add_filter( 'upgrader_post_install', array( $this, 'after_install' ), 10, 3 );
    }

    /**
     * Check for plugin updates — WordPress প্রতি ১২ ঘন্টায় এটি কল করে
     */
    public function check_for_update( $transient ) {
        if ( empty( $transient->checked ) ) {
            return $transient;
        }

        $remote = $this->get_remote_info();

        if ( $remote && version_compare( $this->current_version, $remote->version, '<' ) ) {
            $plugin_data = new stdClass();
            $plugin_data->slug        = $this->plugin_slug;
            $plugin_data->plugin      = $this->plugin_file;
            $plugin_data->new_version = $remote->version;
            $plugin_data->url         = $remote->homepage ?? '';
            $plugin_data->package     = $remote->download_url ?? '';
            $plugin_data->tested      = $remote->tested ?? '6.7';
            $plugin_data->requires    = $remote->requires ?? '5.8';
            $plugin_data->requires_php = $remote->requires_php ?? '7.4';

            $transient->response[ $this->plugin_file ] = $plugin_data;
        }

        return $transient;
    }

    /**
     * Plugin details popup — "View Details" ক্লিক করলে যা দেখায়
     */
    public function plugin_info( $result, $action, $args ) {
        if ( $action !== 'plugin_information' || $args->slug !== $this->plugin_slug ) {
            return $result;
        }

        $remote = $this->get_remote_info();

        if ( ! $remote ) {
            return $result;
        }

        $info = new stdClass();
        $info->name          = 'CAPI Gateway — Server-Side Tracking';
        $info->slug          = $this->plugin_slug;
        $info->version       = $remote->version;
        $info->author        = '<a href="' . esc_url( $remote->homepage ?? '' ) . '">CAPI Gateway</a>';
        $info->homepage      = $remote->homepage ?? '';
        $info->download_link = $remote->download_url ?? '';
        $info->tested        = $remote->tested ?? '6.7';
        $info->requires      = $remote->requires ?? '5.8';
        $info->requires_php  = $remote->requires_php ?? '7.4';
        $info->last_updated  = $remote->last_updated ?? '';
        $info->sections      = array(
            'description'  => $remote->description ?? 'Server-Side Facebook CAPI tracking for WooCommerce.',
            'changelog'    => $remote->changelog ?? '<p>Bug fixes and improvements.</p>',
        );

        // Banner image (optional)
        if ( ! empty( $remote->banner ) ) {
            $info->banners = array( 'high' => $remote->banner );
        }

        return $info;
    }

    /**
     * After install — ফোল্ডার নাম ঠিক করে
     */
    public function after_install( $response, $hook_extra, $result ) {
        global $wp_filesystem;

        if ( ! isset( $hook_extra['plugin'] ) || $hook_extra['plugin'] !== $this->plugin_file ) {
            return $result;
        }

        $install_dir = plugin_dir_path( CAPIGW_PLUGIN_FILE );
        $wp_filesystem->move( $result['destination'], $install_dir );
        $result['destination'] = $install_dir;

        // Re-activate plugin
        activate_plugin( $this->plugin_file );

        return $result;
    }

    /**
     * Fetch remote plugin info from our server — ক্যাশ সহ
     */
    private function get_remote_info() {
        $cache_key = 'capigw_update_info';
        $cached    = get_transient( $cache_key );

        if ( $cached !== false ) {
            return $cached;
        }

        $settings = capigw_get_settings();

        $response = wp_remote_get( $this->update_url, array(
            'timeout'   => 10,
            'sslverify' => false,
            'headers'   => array(
                'X-API-Key'       => $settings['api_key'] ?? '',
                'X-Plugin-Version' => $this->current_version,
            ),
        ) );

        if ( is_wp_error( $response ) || wp_remote_retrieve_response_code( $response ) !== 200 ) {
            return false;
        }

        $body = json_decode( wp_remote_retrieve_body( $response ) );

        if ( empty( $body ) || empty( $body->version ) ) {
            return false;
        }

        // Cache for 12 hours
        set_transient( $cache_key, $body, 12 * HOUR_IN_SECONDS );

        return $body;
    }
}

// Initialize auto-updater
new CAPIGW_Auto_Updater();
