# Buykori AdSync SST Clean Rebuild Plan

এই নোটটি current production code replace করার জন্য নয়। উদ্দেশ্য হলো tracking logic আবার ছোট ছোট ধাপে rebuild করা, যাতে Facebook/TikTok/GA4 event flow কোন ধাপে ভাঙছে সেটা পরিষ্কার দেখা যায়।

## Current Observation

- Tracking logic অনেক জায়গায় ছড়িয়ে গেছে: frontend JS, WordPress REST handler, admin-ajax fallback, WooCommerce order fallback, deferred purchase confirm, FastAPI worker, TikTok mapper।
- একই event একাধিক path দিয়ে যেতে পারে। ফলে duplicate guard, order fallback, deferred purchase, test event code, content_id enrichment আলাদা আলাদা জায়গায় bug তৈরি করতে পারে।
- TikTok `PageView` backend থেকে intentionally পাঠানো হয় না। TikTok test panel-এ reliable check করতে হবে `ViewContent`, `AddToCart`, `InitiateCheckout`, `Purchase` দিয়ে।
- Purchase deferred mode ON থাকলে order place করার সাথে সাথে final `Purchase` যাবে না; order confirm/processing trigger লাগবে।

## Rebuild Rule

প্রতি ধাপে শুধু একটাই logic enable করতে হবে। নতুন ধাপ যোগ করার আগে আগের ধাপের result screenshot/log দিয়ে confirm করতে হবে।

## Phase 0: Freeze

- Live production files আর patch করা হবে না, যতক্ষণ না isolated V2 flow local/live REST test-এ pass করে।
- Existing plugin active থাকবে, কিন্তু V2 file inactive থাকবে।

## Phase 1: Backend Direct Test

Goal: WordPress বাদ দিয়ে FastAPI gateway Facebook/TikTok/GA4-এ event পাঠাতে পারে কিনা verify করা।

Test event:
- `ViewContent`
- `AddToCart`
- `InitiateCheckout`

Required payload:
- `event_name`
- `event_time`
- `event_id`
- `event_source_url`
- `action_source=website`
- `custom_data.content_ids`
- `custom_data.contents`
- `custom_data.content_type=product`
- `custom_data.value`
- `custom_data.currency`
- `user_data.client_ip_address`
- `user_data.client_user_agent`
- `user_data.external_id`
- optional: `em`, `ph`, `ttp`, `ttclid`

Pass condition:
- Meta Test Events receives event.
- TikTok Test Events receives `ViewContent/AddToCart/InitiateCheckout`.
- Backend log has TikTok `code:0` and `test_event_code_used:true`.

## Phase 2: WordPress REST Only

Goal: Browser JS ছাড়া WordPress REST endpoint থেকে gateway hit করা।

Endpoint:
- `/wp-json/buykori/v2/track`

Pass condition:
- REST response success.
- Set-Cookie returns `_fbp`, `_fbc` when fbclid exists, `_ttp`, `_buykorigw_vid`.
- Meta/TikTok both receive `ViewContent`.

## Phase 3: Minimal Browser JS

Goal: Only three browser events:
- `PageView` to Meta/GA4 only
- `ViewContent` to Meta/TikTok/GA4
- `AddToCart` to Meta/TikTok/GA4

Do not add:
- checkout submit hooks
- order fallback
- deferred purchase
- admin-ajax fallback

Pass condition:
- Product page load sends `ViewContent` with content_id.
- Add to cart sends `AddToCart` with content_id.

## Phase 4: InitiateCheckout

Goal: Only one reliable trigger for checkout.

Preferred trigger:
- checkout page first meaningful load if cart has product data

Fallback trigger:
- place order click with synchronous REST call

Pass condition:
- One order flow produces exactly one `InitiateCheckout` event in Meta and TikTok.
- `content_id/content_ids/contents` present.
- email/phone present after checkout fields are filled, when available.

## Phase 5: Purchase

Goal: Purchase handled separately from browser events.

Flow:
- Thank-you page creates pending Purchase if deferred mode ON.
- Processing/completed/manual confirm sends final Purchase.

Pass condition:
- Order note/meta shows pending then confirmed.
- Meta/TikTok receive Purchase only after confirm.

## Phase 6: Remove Old Fallbacks

Only after V2 passes:
- remove duplicate admin-ajax fallback or keep as disabled emergency fallback.
- remove overlapping order InitiateCheckout fallback hooks unless strictly needed.
- keep one dedupe rule per event.

## Debug Commands

PHP syntax:

```powershell
php -l wordpress-plugin\buykori-adsync\includes\tracking-core-v2.php
```

Search active hooks:

```powershell
rg -n "add_action|register_rest_route|InitiateCheckout|Purchase|send_event" wordpress-plugin\buykori-adsync
```

TikTok service test:

```powershell
$env:PYTHONPATH="."; pytest tests\test_tiktok_service.py -q
```
