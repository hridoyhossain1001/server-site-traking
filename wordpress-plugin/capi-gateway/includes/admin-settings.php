<?php
/**
 * CAPI Gateway — Admin Settings Page
 *
 * WordPress Admin প্যানেলে সুন্দর সেটিংস পেজ তৈরি করে।
 * ক্লায়েন্ট শুধু API Key বসাবে, বাকি সব অটোমেটিক।
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ─── Register Admin Menu ───────────────────────────────────────────────────────
add_action( 'admin_menu', 'capigw_admin_menu' );

function capigw_admin_menu() {
    add_menu_page(
        'CAPI Gateway Settings',       // Page title
        'CAPI Gateway',                // Menu title
        'manage_options',              // Capability
        'capi-gateway',                // Menu slug
        'capigw_settings_page',        // Callback function
        'dashicons-chart-area',        // Icon
        58                             // Position
    );
}

// ─── Register Settings ─────────────────────────────────────────────────────────
add_action( 'admin_init', 'capigw_register_settings' );

function capigw_register_settings() {
    register_setting( 'capigw_settings_group', CAPIGW_OPTION_KEY, 'capigw_sanitize_settings' );
}

function capigw_sanitize_settings( $input ) {
    $sanitized = array();
    $sanitized['api_key']            = sanitize_text_field( $input['api_key'] ?? '' );
    $sanitized['gateway_url']        = esc_url_raw( $input['gateway_url'] ?? CAPIGW_DEFAULT_GATEWAY_URL );
    $sanitized['enable_pageview']    = isset( $input['enable_pageview'] ) ? 1 : 0;
    $sanitized['enable_viewcontent'] = isset( $input['enable_viewcontent'] ) ? 1 : 0;
    $sanitized['enable_addtocart']   = isset( $input['enable_addtocart'] ) ? 1 : 0;
    $sanitized['enable_checkout']    = isset( $input['enable_checkout'] ) ? 1 : 0;
    $sanitized['enable_purchase']    = isset( $input['enable_purchase'] ) ? 1 : 0;
    $sanitized['deferred_purchase']  = isset( $input['deferred_purchase'] ) ? 1 : 0;
    $sanitized['auto_confirm_status']= sanitize_text_field( $input['auto_confirm_status'] ?? 'completed' );
    $sanitized['debug_mode']         = isset( $input['debug_mode'] ) ? 1 : 0;
    return $sanitized;
}

// ─── AJAX: Connection Test ─────────────────────────────────────────────────────
add_action( 'wp_ajax_capigw_test_connection', 'capigw_test_connection' );

function capigw_test_connection() {
    check_ajax_referer( 'capigw_nonce', 'nonce' );

    if ( ! current_user_can( 'manage_options' ) ) {
        wp_send_json_error( 'Permission denied' );
    }

    $api_key     = sanitize_text_field( $_POST['api_key'] ?? '' );
    $gateway_url = esc_url_raw( $_POST['gateway_url'] ?? '' );

    if ( empty( $api_key ) || empty( $gateway_url ) ) {
        wp_send_json_error( 'API Key এবং Gateway URL দিন।' );
    }

    // Send a test ping to the gateway health endpoint
    $url = rtrim( $gateway_url, '/' ) . '/health';

    $response = wp_remote_get( $url, array(
        'timeout'   => 30,
        'sslverify' => false,
        'headers'   => array(
            'X-API-Key' => $api_key,
        ),
    ) );

    if ( is_wp_error( $response ) ) {
        wp_send_json_error( 'Connection failed: ' . $response->get_error_message() );
    }

    $code = wp_remote_retrieve_response_code( $response );
    $body = wp_remote_retrieve_body( $response );

    if ( $code === 200 ) {
        wp_send_json_success( 'Connected successfully! Server is online.' );
    } else {
        wp_send_json_error( "Server responded with HTTP $code. Response: $body" );
    }
}

// ─── Settings Page HTML ────────────────────────────────────────────────────────
function capigw_settings_page() {
    $settings = capigw_get_settings();
    $nonce    = wp_create_nonce( 'capigw_nonce' );
    ?>
    <style>
        .capigw-wrap { max-width: 800px; margin: 20px auto; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .capigw-header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #fff; padding: 30px; border-radius: 12px; margin-bottom: 24px; }
        .capigw-header h1 { margin: 0 0 8px; font-size: 26px; font-weight: 700; }
        .capigw-header p { margin: 0; color: #b0b0d0; font-size: 14px; }
        .capigw-header .version { background: rgba(126,87,194,0.3); color: #b39ddb; padding: 3px 10px; border-radius: 20px; font-size: 12px; margin-left: 10px; }
        .capigw-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .capigw-card h2 { margin: 0 0 16px; font-size: 18px; color: #1a1a2e; border-bottom: 2px solid #7e57c2; padding-bottom: 8px; display: inline-block; }
        .capigw-field { margin-bottom: 18px; }
        .capigw-field label { display: block; font-weight: 600; margin-bottom: 6px; color: #333; font-size: 14px; }
        .capigw-field input[type="text"],
        .capigw-field input[type="password"],
        .capigw-field select { width: 100%; padding: 10px 14px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
        .capigw-field input:focus, .capigw-field select:focus { border-color: #7e57c2; outline: none; box-shadow: 0 0 0 3px rgba(126,87,194,0.15); }
        .capigw-field .description { font-size: 12px; color: #888; margin-top: 4px; }
        .capigw-toggle { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
        .capigw-toggle label { font-weight: 500; color: #333; margin: 0; cursor: pointer; }
        .capigw-switch { position: relative; width: 44px; height: 24px; flex-shrink: 0; }
        .capigw-switch input { opacity: 0; width: 0; height: 0; }
        .capigw-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background: #ccc; border-radius: 24px; transition: 0.3s; }
        .capigw-slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: 0.3s; }
        .capigw-switch input:checked + .capigw-slider { background: #7e57c2; }
        .capigw-switch input:checked + .capigw-slider:before { transform: translateX(20px); }
        .capigw-btn { padding: 10px 24px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        .capigw-btn-primary { background: #7e57c2; color: #fff; }
        .capigw-btn-primary:hover { background: #6a3fb5; }
        .capigw-btn-test { background: #16213e; color: #fff; margin-right: 12px; }
        .capigw-btn-test:hover { background: #0f3460; }
        .capigw-status { padding: 12px 16px; border-radius: 8px; margin-top: 12px; display: none; font-size: 13px; }
        .capigw-status.success { display: block; background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
        .capigw-status.error { display: block; background: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
        .capigw-events-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    </style>

    <div class="capigw-wrap">
        <!-- Header -->
        <div class="capigw-header">
            <h1>⚡ CAPI Gateway <span class="version">v<?php echo CAPIGW_VERSION; ?></span></h1>
            <p>Server-Side Facebook CAPI, TikTok & GA4 Tracking for WooCommerce</p>
        </div>

        <form method="post" action="options.php" id="capigw-form">
            <?php settings_fields( 'capigw_settings_group' ); ?>

            <!-- Connection Settings -->
            <div class="capigw-card">
                <h2>🔑 Connection Settings</h2>

                <div class="capigw-field">
                    <label for="capigw_api_key">API Key</label>
                    <input type="password" id="capigw_api_key"
                           name="<?php echo CAPIGW_OPTION_KEY; ?>[api_key]"
                           value="<?php echo esc_attr( $settings['api_key'] ); ?>"
                           placeholder="আপনার CAPI Gateway API Key পেস্ট করুন"
                           autocomplete="off">
                    <p class="description">CAPI Gateway ড্যাশবোর্ড থেকে আপনার API Key কপি করুন।</p>
                </div>

                <div class="capigw-field">
                    <label for="capigw_gateway_url">Gateway URL</label>
                    <input type="text" id="capigw_gateway_url"
                           name="<?php echo CAPIGW_OPTION_KEY; ?>[gateway_url]"
                           value="<?php echo esc_attr( $settings['gateway_url'] ); ?>"
                           placeholder="https://your-gateway.herokuapp.com/api/v1">
                    <p class="description">সাধারণত এটি পরিবর্তন করার দরকার হয় না।</p>
                </div>

                <button type="button" class="capigw-btn capigw-btn-test" id="capigw-test-btn" onclick="capigwTestConnection()">
                    🔍 Test Connection
                </button>
                <div id="capigw-test-status" class="capigw-status"></div>
            </div>

            <!-- Event Tracking Toggles -->
            <div class="capigw-card">
                <h2>📊 Event Tracking</h2>
                <p style="color:#666; font-size:13px; margin-bottom:16px;">কোন কোন ইভেন্ট ট্র্যাক করতে চান সিলেক্ট করুন:</p>

                <div class="capigw-events-grid">
                    <?php
                    $events = array(
                        'enable_pageview'    => array( '👁️ PageView', 'প্রতিটি পেজ ভিজিট ট্র্যাক করে' ),
                        'enable_viewcontent' => array( '🔍 ViewContent', 'প্রোডাক্ট পেজ ভিউ ট্র্যাক করে' ),
                        'enable_addtocart'   => array( '🛒 AddToCart', 'কার্টে প্রোডাক্ট যোগ করা ট্র্যাক করে' ),
                        'enable_checkout'    => array( '💳 InitiateCheckout', 'চেকআউট শুরু করা ট্র্যাক করে' ),
                        'enable_purchase'    => array( '💰 Purchase', 'অর্ডার সম্পন্ন হওয়া ট্র্যাক করে' ),
                    );
                    foreach ( $events as $key => $info ) :
                    ?>
                        <div class="capigw-toggle">
                            <label class="capigw-switch">
                                <input type="checkbox"
                                       name="<?php echo CAPIGW_OPTION_KEY; ?>[<?php echo $key; ?>]"
                                       value="1"
                                       <?php checked( $settings[ $key ], 1 ); ?>>
                                <span class="capigw-slider"></span>
                            </label>
                            <label><?php echo $info[0]; ?></label>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>

            <!-- Deferred Purchase (COD) -->
            <div class="capigw-card">
                <h2>📦 Deferred Purchase (COD Support)</h2>
                <p style="color:#666; font-size:13px; margin-bottom:16px;">
                    ক্যাশ-অন-ডেলিভারি (COD) অর্ডারের জন্য Purchase ইভেন্ট তখনই Facebook-এ পাঠানো হবে যখন অর্ডারের স্ট্যাটাস পরিবর্তন হবে।
                </p>

                <div class="capigw-toggle">
                    <label class="capigw-switch">
                        <input type="checkbox"
                               name="<?php echo CAPIGW_OPTION_KEY; ?>[deferred_purchase]"
                               value="1"
                               <?php checked( $settings['deferred_purchase'], 1 ); ?>>
                        <span class="capigw-slider"></span>
                    </label>
                    <label>Deferred Purchase চালু করুন</label>
                </div>

                <div class="capigw-field">
                    <label for="capigw_auto_confirm">অটো-কনফার্ম স্ট্যাটাস</label>
                    <select id="capigw_auto_confirm"
                            name="<?php echo CAPIGW_OPTION_KEY; ?>[auto_confirm_status]">
                        <option value="processing" <?php selected( $settings['auto_confirm_status'], 'processing' ); ?>>Processing</option>
                        <option value="completed" <?php selected( $settings['auto_confirm_status'], 'completed' ); ?>>Completed</option>
                    </select>
                    <p class="description">এই স্ট্যাটাসে অর্ডার গেলে Purchase event অটোমেটিক Facebook-এ যাবে।</p>
                </div>
            </div>

            <!-- Debug Mode -->
            <div class="capigw-card">
                <h2>🛠️ Advanced</h2>
                <div class="capigw-toggle">
                    <label class="capigw-switch">
                        <input type="checkbox"
                               name="<?php echo CAPIGW_OPTION_KEY; ?>[debug_mode]"
                               value="1"
                               <?php checked( $settings['debug_mode'], 1 ); ?>>
                        <span class="capigw-slider"></span>
                    </label>
                    <label>🐛 Debug Mode (error_log-এ লগ লিখবে)</label>
                </div>
            </div>

            <!-- Save -->
            <p>
                <?php submit_button( '💾 Save Settings', 'capigw-btn capigw-btn-primary', 'submit', false ); ?>
            </p>
        </form>
    </div>

    <script>
    function capigwTestConnection() {
        try {
            var btn = document.getElementById('capigw-test-btn');
            var status = document.getElementById('capigw-test-status');
            var apiKey = document.getElementById('capigw_api_key').value.trim();
            var gatewayUrl = document.getElementById('capigw_gateway_url').value.trim();

            btn.disabled = true;
            btn.textContent = '⏳ Testing...';
            status.style.display = 'none';
            status.className = 'capigw-status';

            if (!apiKey || !gatewayUrl) {
                status.style.display = 'block';
                status.className = 'capigw-status error';
                status.textContent = '❌ দয়া করে API Key এবং Gateway URL দিন।';
                btn.disabled = false;
                btn.textContent = '🔍 Test Connection';
                return;
            }

            var formData = new FormData();
            formData.append('action', 'capigw_test_connection');
            formData.append('nonce', '<?php echo $nonce; ?>');
            formData.append('api_key', apiKey);
            formData.append('gateway_url', gatewayUrl);

            var ajax_url = (typeof ajaxurl !== 'undefined') ? ajaxurl : '/wp-admin/admin-ajax.php';

            fetch(ajax_url, {
                method: 'POST',
                body: formData,
            })
            .then(function(res) { 
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json(); 
            })
            .then(function(data) {
                status.style.display = 'block';
                if (data.success) {
                    status.className = 'capigw-status success';
                    status.innerHTML = '✅ ' + data.data;
                } else {
                    status.className = 'capigw-status error';
                    status.innerHTML = '❌ ' + (data.data || 'Unknown error');
                }
                btn.disabled = false;
                btn.textContent = '🔍 Test Connection';
            })
            .catch(function(err) {
                status.style.display = 'block';
                status.className = 'capigw-status error';
                status.textContent = '❌ Network error: ' + err.message;
                btn.disabled = false;
                btn.textContent = '🔍 Test Connection';
            });
        } catch (e) {
            console.error(e);
            alert("Error: " + e.message);
        }
    }
    </script>
    <?php
}
