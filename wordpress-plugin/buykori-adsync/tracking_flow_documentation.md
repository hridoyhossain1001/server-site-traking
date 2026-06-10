# Buykori AdSync WordPress Plugin Tracking Flow Sequence

This document explains the chronological order and interaction flow of the tracking files in the **Buykori AdSync WordPress Plugin**.

---

## 1. Initialization Phase
* **Files involved:**
  * `buykori-adsync.php` (Main Plugin Entry)
  * `includes/frontend-tracking.php`
  * `assets/js/tracker.js`
* **Flow details:**
  1. WordPress boots up the plugin via `buykori-adsync.php`.
  2. The plugin registers activation/deactivation hooks, HPOS WooCommerce compatibility, and sets up settings.
  3. `includes/frontend-tracking.php` runs `buykorigw_enqueue_tracker_script()` which enqueues `assets/js/tracker.js` to run in the visitor's browser.
  4. The helper function `buykorigw_inject_tracker()` injects a hidden configuration span (`#buykorigw-tracker-config`) at the bottom of the HTML containing settings like API Keys, active tracking events, current currency, current page type (checkout, cart, product, etc.), and active cart/product details.

---

## 2. Visitor Identification Phase
* **Files involved:**
  * `assets/js/tracker.js`
  * `includes/frontend-tracking.php` (AJAX handler)
* **Flow details:**
  1. `tracker.js` runs in the browser. It checks if tracking cookies exist:
     * `_buykorigw_vid` (A persistent first-party unique visitor ID).
     * `_fbp`, `_fbc`, `_ttp`, `_ttclid` (Attribution cookies for Meta & TikTok).
     * If missing, it generates and saves them as 90-day cookies.
  2. If the user logs in, or submits their name/email/phone on the storefront, `tracker.js` triggers an `Identify` event via an AJAX request to `/wp-json/buykori/v1/track` or the admin-ajax handler `buykorigw_ajax_track_event`.
  3. The PHP side normalizes and SHA-256 hashes the PII (Email, Phone, Name, City, etc.) and saves the hashes into cookies for subsequent browser event matching.

---

## 3. Product Browsing Phase
* **Files involved:**
  * `assets/js/tracker.js`
  * `includes/frontend-tracking.php` (AJAX handler)
* **Flow details:**
  1. **PageView Event:** Fires automatically on every page load via JS calling the backend `/track` endpoint.
  2. **ViewContent Event:** If the visitor is on a WooCommerce single product page, the page configuration includes the product information (ID, SKU, Title, Price, Category). `tracker.js` reads this and fires `ViewContent` via AJAX to the FastAPI backend.

---

## 4. Add to Cart Phase
* **Files involved:**
  * `assets/js/tracker.js`
  * `buykori-adsync.php` (`buykorigw_server_add_to_cart` hook)
* **Flow details:**
  1. The user clicks "Add to Cart".
  2. To remain compatible with caching plugins, `tracker.js` intercepts the button click, sets a temporary cookie `_buykorigw_atc_intent`, and triggers the event.
  3. Simultaneously, the backend hook `woocommerce_add_to_cart` receives the request, reads the intent cookie, packages the product details, hashes any available user identity details, and forwards the `AddToCart` event payload to the API Gateway.

---

## 5. Checkout & Incomplete Lead Capture Phase
* **Files involved:**
  * `assets/js/tracker.js`
  * `includes/frontend-tracking.php`
  * `includes/woo-order-hooks.php`
* **Flow details:**
  1. **InitiateCheckout Event:** When the checkout page loads, `tracker.js` reads the current cart contents and fires `InitiateCheckout`. It saves a temporary cookie `_buykorigw_ic_sent` for 20 minutes to prevent sending duplicates if the page is reloaded.
  2. **Incomplete Checkout Capture:** As the user types into form fields (Phone, Email, First Name, Address) at checkout:
     * `tracker.js` debounces and captures the typed inputs.
     * It sends the partial customer details (uncompleted draft) via AJAX to `/wp-json/buykori/v1/incomplete-checkout`.
     * The backend forwards it to the FastAPI endpoint `/incomplete-checkouts/upsert` to store it as a recovery lead.

---

## 6. Purchase & Post-Purchase Phase
* **Files involved:**
  * `includes/woo-order-hooks.php` (Attribution snapshotting)
  * `includes/frontend-tracking.php` (Purchase event scheduler & sender)
  * `buykori-adsync.php`
* **Flow details:**
  1. **Attribution Snapshotting:** During the checkout submission process, before the user is redirected to external payment gateways (like bKash, Nagad, SSLCommerz), `includes/woo-order-hooks.php` captures all user tracking parameters (IP, User Agent, fbp, fbc, ttp, ttclid, UTM campaigns, GA4 IDs) and saves them as **order metadata** in the WooCommerce database (e.g., `_buykorigw_snapshot_fbp`).
  2. **Incomplete Lead Conversion:** When the order is successfully placed, the plugin automatically calls `/incomplete-checkouts/convert` to convert the captured incomplete lead into a completed order.
  3. **Event Scheduling:** Once the order is completed (Thank You page is reached), `buykorigw_schedule_purchase_sync()` is triggered.
     * To prevent slow page load times, it queues the event using Action Scheduler (`as_enqueue_async_action`) or WP-Cron.
  4. **Event Delivery:** The scheduled job calls `buykorigw_track_purchase($order_id)`:
     * It fetches the order details and the previously saved meta snapshots (ensuring accurate attribution even if payment redirects cleared browser cookies).
     * It formats the items, currencies, prices, COD indicators, and recipient details.
     * It hashes all PII details.
     * It sends the `Purchase` event payload to the backend. If `deferred_purchase` is enabled, it appends `?hold=true` to hold the event until the admin changes the order status to "completed".
