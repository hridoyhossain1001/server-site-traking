<?php
/**
 * CAPI Gateway — WooCommerce Order Hooks
 *
 * এটিই মূল সমাধান — "ডাবল কনফার্মেশন" সমস্যা এখানে সমাধান হয়।
 *
 * কাজের ধরন:
 * 1. অর্ডার স্ট্যাটাস "Completed" বা "Processing" হলে অটোমেটিক
 *    CAPI Gateway API-তে confirm রিকোয়েস্ট পাঠায়।
 * 2. API কল ফেইল হলে Action Scheduler দিয়ে retry করে।
 * 3. অর্ডার পেজে একটি Meta Box দেখায় — tracking status বোঝা যায়।
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ─── 1. Order Status Change → Auto Confirm Deferred Purchase ──────────────────
add_action( 'woocommerce_order_status_completed', 'capigw_on_order_status_change', 20, 1 );
add_action( 'woocommerce_order_status_processing', 'capigw_on_order_status_change', 20, 1 );

function capigw_on_order_status_change( $order_id ) {
    $settings = capigw_get_settings();

    // Only proceed if deferred_purchase is ON
    if ( ! $settings['deferred_purchase'] ) {
        return;
    }

    if ( empty( $settings['api_key'] ) || empty( $settings['gateway_url'] ) ) {
        return;
    }

    // Check which status should trigger the confirm
    $current_action = current_action();
    $trigger_status = $settings['auto_confirm_status'] ?? 'completed';

    // Match action to expected trigger status
    if ( $trigger_status === 'completed' && $current_action !== 'woocommerce_order_status_completed' ) {
        return;
    }
    if ( $trigger_status === 'processing' && $current_action !== 'woocommerce_order_status_processing' ) {
        return;
    }

    // Prevent duplicate confirms — use WC_Order for HPOS compatibility
    $order = wc_get_order( $order_id );
    if ( ! $order ) {
        return;
    }

    $already_confirmed = $order->get_meta( '_capigw_confirmed' );
    if ( $already_confirmed ) {
        if ( $settings['debug_mode'] ) {
            error_log( "[CAPI Gateway] Order #$order_id already confirmed, skipping." );
        }
        return;
    }

    // Send confirm request to CAPI Gateway
    $success = capigw_confirm_order( $order_id );

    if ( $success ) {
        $order->update_meta_data( '_capigw_confirmed', 1 );
        $order->update_meta_data( '_capigw_confirmed_at', current_time( 'mysql' ) );
        $order->save();

        if ( $settings['debug_mode'] ) {
            error_log( "[CAPI Gateway] ✅ Order #$order_id auto-confirmed successfully." );
        }
    } else {
        // Schedule retry via Action Scheduler
        capigw_schedule_retry( $order_id );

        $order->update_meta_data( '_capigw_confirm_status', 'retry_scheduled' );
        $order->save();

        if ( $settings['debug_mode'] ) {
            error_log( "[CAPI Gateway] ⚠️ Order #$order_id confirm failed, retry scheduled." );
        }
    }
}


// ─── 2. Confirm API Call ───────────────────────────────────────────────────────
function capigw_confirm_order( $order_id ) {
    $settings = capigw_get_settings();
    $url      = rtrim( $settings['gateway_url'], '/' ) . '/events/confirm';

    $response = wp_remote_post( $url, array(
        'timeout'   => 15,
        'sslverify' => true,
        'headers'   => array(
            'Content-Type' => 'application/json',
            'X-API-Key'    => $settings['api_key'],
            'X-CAPI-Origin'=> capigw_site_origin(),
        ),
        'body'      => wp_json_encode( array(
            'order_id' => (string) $order_id,
        ) ),
    ) );

    if ( is_wp_error( $response ) ) {
        // Critical failure — always log regardless of debug_mode
        error_log( '[CAPI Gateway] Confirm failed for order #' . $order_id . ': ' . $response->get_error_message() );
        return false;
    }

    $code = wp_remote_retrieve_response_code( $response );
    $body = json_decode( wp_remote_retrieve_body( $response ), true );

    if ( $code === 200 && isset( $body['status'] ) && $body['status'] === 'success' ) {
        return true;
    }

    // 404 = no pending event found; do not mark the order confirmed.
    if ( $code === 404 ) {
        if ( $settings['debug_mode'] ) {
            error_log( "[CAPI Gateway] No pending event for order #$order_id (404). Possibly already confirmed." );
        }
        return false;
    }

    // Non-200 or unexpected response — always log
    error_log( "[CAPI Gateway] Confirm HTTP $code for order #$order_id: " . wp_json_encode( $body ) );

    return false;
}


// ─── 3. Action Scheduler Retry Queue ───────────────────────────────────────────
function capigw_schedule_retry( $order_id ) {
    // Use WooCommerce Action Scheduler if available, otherwise WP-Cron
    if ( function_exists( 'as_schedule_single_action' ) ) {
        if (
            function_exists( 'as_next_scheduled_action' )
            && as_next_scheduled_action( 'capigw_retry_confirm', array( 'order_id' => $order_id ), 'capi-gateway' )
        ) {
            return;
        }

        // Retry after 5 minutes
        as_schedule_single_action(
            time() + 300,
            'capigw_retry_confirm',
            array( 'order_id' => $order_id ),
            'capi-gateway'
        );
    } else {
        if ( wp_next_scheduled( 'capigw_retry_confirm_cron', array( $order_id ) ) ) {
            return;
        }

        // Fallback: WP-Cron
        wp_schedule_single_event(
            time() + 300,
            'capigw_retry_confirm_cron',
            array( $order_id )
        );
    }
}

// Action Scheduler callback
add_action( 'capigw_retry_confirm', 'capigw_retry_confirm_handler' );

function capigw_retry_confirm_handler( $args ) {
    $order_id = $args['order_id'] ?? 0;
    if ( ! $order_id ) {
        return;
    }

    $settings = capigw_get_settings();

    // Already confirmed? Skip
    if ( capigw_get_order_meta( $order_id, '_capigw_confirmed' ) ) {
        return;
    }

    $retry_count = (int) capigw_get_order_meta( $order_id, '_capigw_retry_count' );

    $success = capigw_confirm_order( $order_id );

    if ( $success ) {
        capigw_update_order_meta( $order_id, '_capigw_confirmed', 1 );
        capigw_update_order_meta( $order_id, '_capigw_confirmed_at', current_time( 'mysql' ) );
        capigw_update_order_meta( $order_id, '_capigw_confirm_status', 'confirmed' );

        if ( $settings['debug_mode'] ) {
            error_log( "[CAPI Gateway] ✅ Retry success for order #$order_id (attempt $retry_count)" );
        }
    } else {
        $retry_count++;
        capigw_update_order_meta( $order_id, '_capigw_retry_count', $retry_count );

        // Max 5 retries (5min, 10min, 20min, 40min, 80min)
        if ( $retry_count < 5 ) {
            $delay = 300 * pow( 2, $retry_count - 1 ); // Exponential backoff
            if ( function_exists( 'as_schedule_single_action' ) ) {
                if (
                    ! function_exists( 'as_next_scheduled_action' )
                    || ! as_next_scheduled_action( 'capigw_retry_confirm', array( 'order_id' => $order_id ), 'capi-gateway' )
                ) {
                    as_schedule_single_action(
                        time() + $delay,
                        'capigw_retry_confirm',
                        array( 'order_id' => $order_id ),
                        'capi-gateway'
                    );
                }
            } elseif ( ! wp_next_scheduled( 'capigw_retry_confirm_cron', array( $order_id ) ) ) {
                wp_schedule_single_event(
                    time() + $delay,
                    'capigw_retry_confirm_cron',
                    array( $order_id )
                );
            }
            capigw_update_order_meta( $order_id, '_capigw_confirm_status', 'retry_' . $retry_count );

            if ( $settings['debug_mode'] ) {
                error_log( "[CAPI Gateway] Retry #$retry_count for order #$order_id, next in {$delay}s" );
            }
        } else {
            capigw_update_order_meta( $order_id, '_capigw_confirm_status', 'failed' );

            if ( $settings['debug_mode'] ) {
                error_log( "[CAPI Gateway] ❌ Max retries reached for order #$order_id" );
            }
        }
    }
}

// WP-Cron fallback callback
add_action( 'capigw_retry_confirm_cron', 'capigw_retry_confirm_cron_handler' );

function capigw_retry_confirm_cron_handler( $order_id ) {
    capigw_retry_confirm_handler( array( 'order_id' => $order_id ) );
}


// ─── 4. Admin Order Meta Box — Tracking Status ─────────────────────────────────
add_action( 'add_meta_boxes', 'capigw_add_order_meta_box' );

function capigw_add_order_meta_box() {
    // Support both legacy (post) and HPOS (woocommerce_page_wc-orders) screens
    $screens = array( 'shop_order', 'woocommerce_page_wc-orders' );
    foreach ( $screens as $screen ) {
        add_meta_box(
            'capigw_tracking_status',
            '⚡ CAPI Gateway — Tracking Status',
            'capigw_render_order_meta_box',
            $screen,
            'side',
            'default'
        );
    }
}

function capigw_render_order_meta_box( $post_or_order ) {
    // Support both legacy and HPOS
    if ( $post_or_order instanceof WP_Post ) {
        $order_id = $post_or_order->ID;
    } elseif ( is_a( $post_or_order, 'WC_Order' ) ) {
        $order_id = $post_or_order->get_id();
    } else {
        $order_id = 0;
    }

    if ( ! $order_id ) {
        echo '<p style="color:#999;">Order ID not found.</p>';
        return;
    }

    // Use WC_Order for HPOS compatibility
    $order = wc_get_order( $order_id );
    if ( $order ) {
        $tracked      = $order->get_meta( '_capigw_tracked' );
        $confirmed    = $order->get_meta( '_capigw_confirmed' );
        $confirmed_at = $order->get_meta( '_capigw_confirmed_at' );
        $status       = $order->get_meta( '_capigw_confirm_status' );
        $retry_count  = $order->get_meta( '_capigw_retry_count' );
    } else {
        $tracked = $confirmed = $confirmed_at = $status = $retry_count = '';
    }
    $settings     = capigw_get_settings();

    echo '<div style="font-size:13px; line-height:1.8;">';

    // Purchase event tracked?
    if ( $tracked ) {
        echo '<div style="color:#2e7d32;">✅ Purchase event tracked</div>';
    } else {
        echo '<div style="color:#999;">⏳ Purchase event not yet tracked</div>';
    }

    // Deferred purchase info
    if ( $settings['deferred_purchase'] ) {
        echo '<hr style="border:none; border-top:1px solid #eee; margin:8px 0;">';

        if ( $confirmed ) {
            echo '<div style="color:#2e7d32;">✅ Confirmed & sent to Facebook</div>';
            if ( $confirmed_at ) {
                echo '<div style="color:#666; font-size:11px;">📅 ' . esc_html( $confirmed_at ) . '</div>';
            }
        } elseif ( $status === 'failed' ) {
            echo '<div style="color:#c62828;">❌ Confirm failed (max retries reached)</div>';
            echo '<div style="margin-top:6px;"><button type="button" class="button button-small" onclick="capigwManualConfirm(' . $order_id . ', this)">🔄 Retry Now</button></div>';
        } elseif ( strpos( $status, 'retry' ) !== false ) {
            echo '<div style="color:#f57c00;">⏳ Retry in progress (attempt ' . intval( $retry_count ) . '/5)</div>';
        } else {
            echo '<div style="color:#1565c0;">📦 Pending — waiting for order status change</div>';
            echo '<div style="color:#999; font-size:11px;">Auto-confirm on: <strong>' . esc_html( ucfirst( $settings['auto_confirm_status'] ) ) . '</strong></div>';
        }
    }

    echo '</div>';

    // Manual retry button JS
    ?>
    <script>
    function capigwManualConfirm(orderId, btn) {
        btn = btn || (typeof event !== 'undefined' ? event.target : null);
        if (!btn) return;
        if (!confirm('Order #' + orderId + ' এর Purchase event আবার পাঠাতে চান?')) return;
        btn.disabled = true;
        btn.textContent = '⏳ Sending...';

        fetch(ajaxurl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'action=capigw_manual_confirm&order_id=' + orderId + '&nonce=<?php echo wp_create_nonce( "capigw_manual_confirm" ); ?>'
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                btn.textContent = '✅ Sent!';
                btn.style.color = '#2e7d32';
            } else {
                btn.textContent = '❌ Failed';
                btn.disabled = false;
            }
        })
        .catch(function() {
            btn.textContent = '❌ Error';
            btn.disabled = false;
        });
    }
    </script>
    <?php
}


// ─── 5. AJAX: Manual Confirm from Meta Box ─────────────────────────────────────
add_action( 'wp_ajax_capigw_manual_confirm', 'capigw_ajax_manual_confirm' );

function capigw_ajax_manual_confirm() {
    check_ajax_referer( 'capigw_manual_confirm', 'nonce' );

    if ( ! current_user_can( 'manage_woocommerce' ) ) {
        wp_send_json_error( 'Permission denied' );
    }

    $order_id = intval( $_POST['order_id'] ?? 0 );
    if ( ! $order_id ) {
        wp_send_json_error( 'Invalid order ID' );
    }

    $success = capigw_confirm_order( $order_id );

    if ( $success ) {
        capigw_update_order_meta( $order_id, '_capigw_confirmed', 1 );
        capigw_update_order_meta( $order_id, '_capigw_confirmed_at', current_time( 'mysql' ) );
        capigw_update_order_meta( $order_id, '_capigw_confirm_status', 'confirmed' );
        wp_send_json_success( 'Order confirmed!' );
    } else {
        wp_send_json_error( 'Confirm failed' );
    }
}
