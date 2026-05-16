<?php
/**
 * Fired when the plugin is uninstalled.
 *
 * @package CAPI_Gateway
 */

// If uninstall not called from WordPress, then exit.
if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
	exit;
}

// 1. Delete Database Options
delete_option( 'capigw_settings' );
delete_option( 'capigw_custom_events' );

// 2. Delete Transients (if any, although plugin doesn't use transients yet, good practice)
delete_transient( 'capigw_update_info' );

// 3. Clear Scheduled Actions (WP-Cron)
$timestamp = wp_next_scheduled( 'capigw_retry_confirm_cron' );
if ( $timestamp ) {
	wp_unschedule_event( $timestamp, 'capigw_retry_confirm_cron' );
}

// Action Scheduler actions will be cleaned up by Action Scheduler itself over time,
// but we can explicitly cancel pending actions if Action Scheduler is active.
if ( function_exists( 'as_unschedule_all_actions' ) ) {
	as_unschedule_all_actions( 'capigw_retry_confirm' );
}

// Note: We deliberately do NOT delete order meta data (_capigw_tracked, etc.)
// because order history and tracking status should be preserved even if the 
// plugin is temporarily uninstalled or replaced.
