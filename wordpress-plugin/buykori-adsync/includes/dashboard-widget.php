<?php
/**
 * Buykori AdSync — Dashboard Widget
 *
 * WordPress Admin হোমপেজে একটি সুন্দর ড্যাশবোর্ড উইজেট দেখায়।
 * আজকের ট্র্যাকিং সামারি — মোট ইভেন্ট, সাকসেস রেট, টপ ইভেন্ট, কানেকশন স্ট্যাটাস।
 */

if (!defined('ABSPATH')) {
    exit;
}

// ─── Register Dashboard Widget ─────────────────────────────────────────────────
add_action('wp_dashboard_setup', 'buykorigw_add_dashboard_widget');
add_action('admin_enqueue_scripts', 'buykorigw_dashboard_widget_assets');

function buykorigw_dashboard_widget_assets($hook)
{
    if ($hook !== 'index.php') {
        return;
    }

    $settings = buykorigw_get_settings();
    if (empty($settings['api_key'])) {
        return;
    }

    wp_enqueue_style(
        'buykorigw-dashboard-widget',
        BUYKORIGW_PLUGIN_URL . 'assets/css/dashboard-widget.css',
        array(),
        BUYKORIGW_VERSION
    );

    wp_enqueue_script(
        'buykorigw-dashboard-widget',
        BUYKORIGW_PLUGIN_URL . 'assets/js/dashboard-widget.js',
        array(),
        BUYKORIGW_VERSION,
        true
    );
}

function buykorigw_add_dashboard_widget()
{
    $settings = buykorigw_get_settings();
    if (empty($settings['api_key'])) {
        return;
    }

    wp_add_dashboard_widget(
        'buykorigw_dashboard_widget',
        '⚡ Buykori AdSync — Tracking Overview',
        'buykorigw_dashboard_widget_render'
    );
}

// ─── Widget Render ─────────────────────────────────────────────────────────────
function buykorigw_dashboard_widget_render()
{
    ?>
    <div class="cgw-wrap" data-cgw-nonce="<?php echo esc_attr(wp_create_nonce('buykorigw_widget_nonce')); ?>">
        <div id="cgw-content">
            <div class="cgw-loading">
                <div class="cgw-spinner"></div>
                <span>Loading tracking data...</span>
            </div>
        </div>
        <div class="cgw-footer">
            <a href="<?php echo esc_url(admin_url('admin.php?page=buykori-adsync')); ?>">Plugin Settings</a>
        </div>
    </div>
    <?php
}
// ─── AJAX: Fetch Widget Data ───────────────────────────────────────────────────
add_action('wp_ajax_buykorigw_widget_data', 'buykorigw_widget_data');

function buykorigw_widget_data()
{
    check_ajax_referer('buykorigw_widget_nonce', 'nonce');

    if (!current_user_can('manage_options')) {
        wp_send_json_error('Permission denied');
    }

    $settings = buykorigw_get_settings();

    if (empty($settings['api_key']) || empty($settings['gateway_url'])) {
        wp_send_json_error('API Key not configured');
    }

    // Fetch overview from gateway analytics API
    $base_url = rtrim($settings['gateway_url'], '/');
    $data = array(
        'server_online' => false,
        'total_today' => 0,
        'total_month' => 0,
        'success_rate' => 0,
        'pending_orders' => 0,
        'verified_purchases' => 0,
        'cancelled_or_expired' => 0,
        'pending_value' => 0,
        'pending_oldest_age_hours' => null,
        'top_events' => array(),
    );

    // 1. Check server health
    $health = wp_remote_get($base_url . '/health', array(
        'timeout' => 5,
        'sslverify' => true,
        'headers' => array('X-API-Key' => $settings['api_key']),
    ));

    if (!is_wp_error($health) && wp_remote_retrieve_response_code($health) === 200) {
        $data['server_online'] = true;
    }

    // 2. Get analytics overview (today)
    $overview = wp_remote_get($base_url . '/analytics/overview?days=1', array(
        'timeout' => 8,
        'sslverify' => true,
        'headers' => array('X-API-Key' => $settings['api_key']),
    ));

    if (!is_wp_error($overview) && wp_remote_retrieve_response_code($overview) === 200) {
        $body = json_decode(wp_remote_retrieve_body($overview), true);

        if ($body) {
            $data['total_today'] = $body['total_events'] ?? 0;
            $data['success_rate'] = $body['success_rate'] ?? 0;

            // Top events from breakdown
            if (!empty($body['event_breakdown'])) {
                $top = array_slice($body['event_breakdown'], 0, 5);
                foreach ($top as $ev) {
                    $data['top_events'][] = array(
                        'name' => $ev['event_name'] ?? 'Unknown',
                        'count' => $ev['count'] ?? 0,
                    );
                }
            }
        }
    }

    // 3. Get monthly total (30 days)
    $monthly = wp_remote_get($base_url . '/analytics/overview?days=30', array(
        'timeout' => 8,
        'sslverify' => true,
        'headers' => array('X-API-Key' => $settings['api_key']),
    ));

    if (!is_wp_error($monthly) && wp_remote_retrieve_response_code($monthly) === 200) {
        $mbody = json_decode(wp_remote_retrieve_body($monthly), true);
        if ($mbody) {
            $data['total_month'] = $mbody['total_events'] ?? 0;
        }
    }

    // 4. Get verified purchase / COD summary
    $pending_summary = wp_remote_get($base_url . '/events/deferred/summary', array(
        'timeout' => 5,
        'sslverify' => true,
        'headers' => array('X-API-Key' => $settings['api_key']),
    ));

    if (!is_wp_error($pending_summary) && wp_remote_retrieve_response_code($pending_summary) === 200) {
        $pbody = json_decode(wp_remote_retrieve_body($pending_summary), true);
        if ($pbody) {
            $data['pending_orders'] = $pbody['pending'] ?? 0;
            $data['verified_purchases'] = $pbody['confirmed'] ?? 0;
            $data['cancelled_or_expired'] = ($pbody['cancelled'] ?? 0) + ($pbody['expired'] ?? 0);
            $data['pending_value'] = $pbody['pending_value'] ?? 0;
            $data['pending_oldest_age_hours'] = $pbody['pending_oldest_age_hours'] ?? null;
        }
    } else {
        // Backward-compatible fallback for older servers.
        $pending = wp_remote_get($base_url . '/events/pending?limit=1', array(
            'timeout' => 5,
            'sslverify' => true,
            'headers' => array('X-API-Key' => $settings['api_key']),
        ));

        if (!is_wp_error($pending) && wp_remote_retrieve_response_code($pending) === 200) {
            $pbody = json_decode(wp_remote_retrieve_body($pending), true);
            if ($pbody) {
                $data['pending_orders'] = $pbody['total'] ?? 0;
            }
        }
    }

    wp_send_json_success($data);
}
