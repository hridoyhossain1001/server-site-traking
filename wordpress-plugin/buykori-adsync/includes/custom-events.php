<?php
/**
 * Buykori AdSync — Custom Event Builder
 *
 * ক্লায়েন্ট WordPress Admin থেকে নিজের কাস্টম ইভেন্ট তৈরি করতে পারবে।
 * উদাহরণ: "WishlistAdd", "CouponUsed", "VideoWatch" ইত্যাদি।
 *
 * প্রতিটি কাস্টম ইভেন্টের জন্য সেট করা যায়:
 * - Event Name (যেমন: WishlistAdd)
 * - Trigger Type: CSS Selector Click, Page URL Match, বা Form Submit
 * - CSS Selector (যেমন: .wishlist-btn, #coupon-apply)
 * - URL Pattern (যেমন: /thank-you/, /contact-success/)
 * - Custom Data Fields (value, currency, etc.)
 */

if (!defined('ABSPATH')) {
    exit;
}

// ─── Custom Events Option Key ──────────────────────────────────────────────────
define('BUYKORIGW_CUSTOM_EVENTS_KEY', 'buykorigw_custom_events');

// ─── Register Admin Sub-Page ───────────────────────────────────────────────────
add_action('admin_menu', 'buykorigw_custom_events_menu');
add_action('admin_enqueue_scripts', 'buykorigw_custom_events_admin_assets');

function buykorigw_custom_events_menu()
{
    add_submenu_page(
        'buykori-adsync',                    // Parent slug
        'Custom Event Builder',            // Page title
        '🎯 Custom Events',               // Menu title
        'manage_options',                  // Capability
        'buykorigw-custom-events',            // Menu slug
        'buykorigw_custom_events_page'        // Callback
    );
}

function buykorigw_custom_events_admin_assets($hook)
{
    if ($hook !== 'buykori-adsync_page_buykorigw-custom-events') {
        return;
    }

    wp_enqueue_style(
        'buykorigw-custom-events-admin',
        BUYKORIGW_PLUGIN_URL . 'assets/css/custom-events-admin.css',
        array(),
        BUYKORIGW_VERSION
    );

    wp_enqueue_script(
        'buykorigw-custom-events-admin',
        BUYKORIGW_PLUGIN_URL . 'assets/js/custom-events-admin.js',
        array(),
        BUYKORIGW_VERSION,
        true
    );
}

// ─── Save Custom Events via AJAX ───────────────────────────────────────────────
add_action('wp_ajax_buykorigw_save_custom_events', 'buykorigw_save_custom_events');

function buykorigw_save_custom_events()
{
    check_ajax_referer('buykorigw_custom_events_nonce', 'nonce');

    if (!current_user_can('manage_options')) {
        wp_send_json_error('Permission denied');
    }

    $raw = $_POST['events'] ?? '[]';
    $events = json_decode(wp_unslash($raw), true);

    if (!is_array($events)) {
        wp_send_json_error('Invalid data');
    }

    // Sanitize each event
    $sanitized = array();
    foreach ($events as $event) {
        $sanitized[] = array(
            'name' => preg_replace('/[^A-Za-z0-9_]/', '', sanitize_text_field($event['name'] ?? '')),
            'trigger' => sanitize_text_field($event['trigger'] ?? 'click'),
            'selector' => sanitize_text_field($event['selector'] ?? ''),
            'url_pattern' => sanitize_text_field($event['url_pattern'] ?? ''),
            'value' => floatval($event['value'] ?? 0),
            'currency' => sanitize_text_field($event['currency'] ?? ''),
            'custom_param' => sanitize_text_field($event['custom_param'] ?? ''),
            'enabled' => (bool) ($event['enabled'] ?? true),
        );
    }

    update_option(BUYKORIGW_CUSTOM_EVENTS_KEY, $sanitized);
    wp_send_json_success('Events saved!');
}

// ─── Settings Page ─────────────────────────────────────────────────────────────
function buykorigw_custom_events_page()
{
    $events = get_option(BUYKORIGW_CUSTOM_EVENTS_KEY, array());
    ?>
    <div class="ceb-wrap"
         data-ceb-events="<?php echo esc_attr(wp_json_encode($events)); ?>"
         data-ceb-nonce="<?php echo esc_attr(wp_create_nonce('buykorigw_custom_events_nonce')); ?>">
        <div class="ceb-header">
            <h1>Custom Event Builder</h1>
            <p>Create custom tracking events using CSS selectors, URL patterns, forms, or timer rules.</p>
        </div>

        <div id="ceb-events-list"></div>

        <div class="ceb-actions">
            <button type="button" class="ceb-btn ceb-btn-add" data-ceb-action="add">Add New Event</button>
            <button type="button" class="ceb-btn ceb-btn-save" data-ceb-action="save">Save All Events</button>
        </div>
        <div id="ceb-status" class="ceb-status"></div>
    </div>
    <?php
}

// ─── Frontend: Inject Custom Event Tracking JS ─────────────────────────────────
add_action('wp_enqueue_scripts', 'buykorigw_custom_events_frontend_assets');
add_action('wp_footer', 'buykorigw_inject_custom_events_js', 99);

function buykorigw_get_active_custom_events()
{
    $settings = buykorigw_get_settings();
    if (empty($settings['api_key'])) {
        return array();
    }

    $events = get_option(BUYKORIGW_CUSTOM_EVENTS_KEY, array());
    if (empty($events)) {
        return array();
    }

    return array_values(array_filter($events, function ($event) {
        return !empty($event['enabled']) && !empty($event['name']);
    }));
}

function buykorigw_custom_events_frontend_assets()
{
    if (empty(buykorigw_get_active_custom_events())) {
        return;
    }

    wp_enqueue_script(
        'buykorigw-custom-events-tracker',
        BUYKORIGW_PLUGIN_URL . 'assets/js/custom-events-tracker.js',
        array(),
        BUYKORIGW_VERSION,
        true
    );
}

function buykorigw_inject_custom_events_js()
{
    $active = buykorigw_get_active_custom_events();
    if (empty($active)) {
        return;
    }

    echo '<span id="buykorigw-custom-events-data" hidden data-events="' . esc_attr(wp_json_encode($active)) . '"></span>';
}
