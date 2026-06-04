# Staging Test Checklist

Run this on a staging WordPress site before a production plugin release.

## Plugin Update Flow

- Install the current working plugin.
- Configure AdSync API URL and API Key.
- Trigger update check from WordPress Dashboard.
- Confirm the update appears with the expected version.
- Click update.
- Confirm the plugin remains active after update.
- Confirm the plugin settings are preserved.

## Tracking Flow

- Test connection from Buykori AdSync settings.
- Visit the storefront homepage and confirm PageView reaches the gateway.
- Open a product page and confirm ViewContent.
- Add a product to cart and confirm AddToCart.
- Start checkout and confirm InitiateCheckout.
- Place a test order and confirm Purchase behavior.

## Deferred Purchase

- Enable Deferred Purchase.
- Place a test order.
- Confirm Purchase is held in pending state.
- Change order status to the configured confirm status.
- Confirm pending Purchase is sent once.
- Confirm duplicate order status changes do not send duplicates.

## Courier Booking Queue

- Enable Courier auto-send for the test client.
- Configure one staging courier provider credential set.
- Place a test COD order.
- Confirm the WordPress/admin action returns quickly without waiting for provider booking.
- Confirm the client portal order shows a queued/processing courier state first.
- Confirm the admin portal Courier Queue tab shows the job.
- Confirm the job moves from `queued` to `processing` to `sent`.
- Confirm the courier order receives provider order/tracking IDs.
- Cancel one queued test order before the worker claims it and confirm no provider booking is sent.
- For a controlled failed-provider test, confirm the job becomes `dead`, Retry requeues it, and successful processing clears the critical alert.

## Backend Smoke Script

- Run read-only backend smoke checks:
  `python scripts\ops\staging_smoke_check.py --base-url https://api.buykori.app --admin-api-key <ADMIN_API_KEY>`
- If the queue intentionally has dead jobs during testing, rerun with `--allow-queue-alerts` only after recording the job IDs.

## Security Checks

- Confirm invalid Origin/Referer AJAX requests are rejected.
- Confirm server-to-server event requests include `X-CAPI-Origin`.
- Confirm SSL verification passes with the production/staging HTTPS domain.
- Confirm plugin update fails if package hash/signature is wrong.
