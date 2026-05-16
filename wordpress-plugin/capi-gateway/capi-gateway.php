<?php
/**
 * Plugin Name:       CAPI Gateway — Server-Side Tracking
 * Plugin URI:        https://still-stream-48626-bb0ac4cda957.herokuapp.com/
 * Description:       Server-Side Facebook CAPI, TikTok, and GA4 tracking for WooCommerce. Auto-tracks PageView, ViewContent, AddToCart, InitiateCheckout, and Purchase events with SHA-256 PII hashing and deferred purchase support.
 * Version:           1.1.1
 * Requires at least: 5.8
 * Requires PHP:      7.4
 * Author:            CAPI Gateway
 * Author URI:        https://still-stream-48626-bb0ac4cda957.herokuapp.com/
 * License:           GPL v2 or later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       capi-gateway
 * WC requires at least: 5.0
 * WC tested up to:   9.0
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Exit if accessed directly
}

// ─── Plugin Constants ──────────────────────────────────────────────────────────
define( 'CAPIGW_VERSION', '1.1.1' );
define( 'CAPIGW_PLUGIN_FILE', __FILE__ );
define( 'CAPIGW_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );
define( 'CAPIGW_PLUGIN_URL', plugin_dir_url( __FILE__ ) );
define( 'CAPIGW_OPTION_KEY', 'capigw_settings' );

// Default Gateway URL (your Heroku server)
define( 'CAPIGW_DEFAULT_GATEWAY_URL', 'https://still-stream-48626-bb0ac4cda957.herokuapp.com/api/v1' );

// ─── Declare WooCommerce HPOS & Blocks Compatibility ──────────────────────────
add_action( 'before_woocommerce_init', function() {
    if ( class_exists( '\Automattic\WooCommerce\Utilities\FeaturesUtil' ) ) {
        \Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility(
            'custom_order_tables', CAPIGW_PLUGIN_FILE, true
        );
        \Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility(
            'cart_checkout_blocks', CAPIGW_PLUGIN_FILE, true
        );
    }
} );

// ─── Activation Hook ───────────────────────────────────────────────────────────
register_activation_hook( __FILE__, 'capigw_activate' );

function capigw_activate() {
    // Set default options if not already set
    if ( ! get_option( CAPIGW_OPTION_KEY ) ) {
        $defaults = array(
            'api_key'           => '',
            'gateway_url'       => CAPIGW_DEFAULT_GATEWAY_URL,
            'enable_pageview'   => 1,
            'enable_viewcontent'=> 1,
            'enable_addtocart'  => 1,
            'enable_checkout'   => 1,
            'enable_purchase'   => 1,
            'deferred_purchase' => 0,  // 1 = hold purchase until order completed
            'auto_confirm_status' => 'completed', // wc status that triggers confirm
            'debug_mode'        => 0,
        );
        update_option( CAPIGW_OPTION_KEY, $defaults );
    }
}

// ─── Deactivation Hook ─────────────────────────────────────────────────────────
register_deactivation_hook( __FILE__, 'capigw_deactivate' );

function capigw_deactivate() {
    // Clean up scheduled actions if any
    if ( function_exists( 'as_unschedule_all_actions' ) ) {
        as_unschedule_all_actions( 'capigw_retry_confirm' );
    }
}

// ─── Helper: Get Plugin Settings ───────────────────────────────────────────────
function capigw_get_settings() {
    $settings = get_option( CAPIGW_OPTION_KEY, array() );
    return wp_parse_args( $settings, array(
        'api_key'           => '',
        'gateway_url'       => CAPIGW_DEFAULT_GATEWAY_URL,
        'enable_pageview'   => 1,
        'enable_viewcontent'=> 1,
        'enable_addtocart'  => 1,
        'enable_checkout'   => 1,
        'enable_purchase'   => 1,
        'deferred_purchase' => 0,
        'auto_confirm_status' => 'completed',
        'debug_mode'        => 0,
    ) );
}

// ─── Helper: Send Event to Gateway (Server-Side via wp_remote_post) ────────────
function capigw_send_event( $event_data, $blocking = true ) {
    $settings = capigw_get_settings();

    if ( empty( $settings['api_key'] ) || empty( $settings['gateway_url'] ) ) {
        if ( $settings['debug_mode'] ) {
            error_log( '[CAPI Gateway] API Key or Gateway URL is missing.' );
        }
        return false;
    }

    $url = rtrim( $settings['gateway_url'], '/' ) . '/events';

    $body = wp_json_encode( array( 'data' => array( $event_data ) ) );

    $response = wp_remote_post( $url, array(
        'timeout'     => 10,
        'redirection' => 0,
        'httpversion' => '1.1',
        'blocking'    => (bool) $blocking,
        'sslverify'   => false,
        'headers'     => array(
            'Content-Type' => 'application/json',
            'X-API-Key'    => $settings['api_key'],
        ),
        'body'        => $body,
    ) );

    if ( is_wp_error( $response ) ) {
        if ( $settings['debug_mode'] ) {
            error_log( '[CAPI Gateway] Send failed: ' . $response->get_error_message() );
        }
        return false;
    }

    if ( $blocking ) {
        $code = wp_remote_retrieve_response_code( $response );
        if ( $code < 200 || $code >= 300 ) {
            if ( $settings['debug_mode'] ) {
                error_log( '[CAPI Gateway] Send HTTP ' . $code . ': ' . wp_remote_retrieve_body( $response ) );
            }
            return false;
        }
    }

    return true;
}

// ─── Helper: SHA-256 Hash (for PII fields) ─────────────────────────────────────
function capigw_hash( $value ) {
    if ( empty( $value ) ) {
        return '';
    }
    $value = strtolower( trim( $value ) );
    // Don't double-hash (already hashed values are 64 chars hex)
    if ( preg_match( '/^[a-f0-9]{64}$/', $value ) ) {
        return $value;
    }
    return hash( 'sha256', $value );
}

function capigw_hash_phone( $value ) {
    if ( empty( $value ) ) {
        return '';
    }
    $value = strtolower( trim( $value ) );
    if ( preg_match( '/^[a-f0-9]{64}$/', $value ) ) {
        return $value;
    }
    $value = preg_replace( '/[^0-9]/', '', $value );
    $value = ltrim( $value, '0' );
    return capigw_hash( $value );
}

// ─── Load Sub-Modules ──────────────────────────────────────────────────────────
function capigw_get_order_meta( $order_id, $key ) {
    if ( function_exists( 'wc_get_order' ) ) {
        $order = wc_get_order( $order_id );
        if ( $order ) {
            return $order->get_meta( $key, true );
        }
    }

    return get_post_meta( $order_id, $key, true );
}

function capigw_update_order_meta( $order_id, $key, $value ) {
    if ( function_exists( 'wc_get_order' ) ) {
        $order = wc_get_order( $order_id );
        if ( $order ) {
            $order->update_meta_data( $key, $value );
            $order->save();
            return;
        }
    }

    update_post_meta( $order_id, $key, $value );
}

// Admin settings page
if ( is_admin() ) {
    require_once CAPIGW_PLUGIN_DIR . 'includes/admin-settings.php';
    require_once CAPIGW_PLUGIN_DIR . 'includes/dashboard-widget.php';
}

// Frontend tracking (only on frontend, not admin/cron, but allow AJAX)
if ( ! is_admin() || wp_doing_ajax() ) {
    require_once CAPIGW_PLUGIN_DIR . 'includes/frontend-tracking.php';
}

// Custom events (admin UI + frontend JS — loads in both contexts)
require_once CAPIGW_PLUGIN_DIR . 'includes/custom-events.php';

// WooCommerce order hooks (always load — works via WP-Cron and admin)
if ( class_exists( 'WooCommerce' ) || in_array( 'woocommerce/woocommerce.php', apply_filters( 'active_plugins', get_option( 'active_plugins' ) ) ) ) {
    require_once CAPIGW_PLUGIN_DIR . 'includes/woo-order-hooks.php';
}

// Auto-updater (check for plugin updates from our server)
if ( is_admin() ) {
    require_once CAPIGW_PLUGIN_DIR . 'includes/auto-updater.php';
}
