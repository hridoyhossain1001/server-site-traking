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

## Security Checks

- Confirm invalid Origin/Referer AJAX requests are rejected.
- Confirm server-to-server event requests include `X-CAPI-Origin`.
- Confirm SSL verification passes with the production/staging HTTPS domain.
- Confirm plugin update fails if package hash/signature is wrong.
