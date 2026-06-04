# Buykori AdSync 360 Codebase Audit Report

Date: 2026-06-03
Last updated: 2026-06-04
Scope: FastAPI backend, client portal, admin portal, WordPress plugin, deploy scripts, nginx config, tests, dependency posture.

## Executive Summary

The codebase has several strong controls already in place: encrypted secrets with production fail-closed behavior, docs disabled by default, TrustedHost middleware, separated CORS behavior for tracker versus portal APIs, client cookie origin checks, signed plugin/site proof for event ingestion, quota/rate-limit logic, WordPress nonce/capability checks, and signed plugin update verification.

The highest-risk items are operational/security posture issues rather than broken business logic: a live server credential is hardcoded in repository instructions, admin password verification still allows plaintext or unsalted SHA256, Starlette is below current security baselines while the app serves static files/downloads, and deploy scripts trust SSH host keys automatically while defaulting to root. These should be fixed before further production growth.

Update 2026-06-04: the repository instruction credential was removed, admin password verification was moved to PBKDF2-only in production, request-size guards were added for public tracking/webhook paths, unsafe plugin-connect cancel redirects were blocked, WordPress admin status rendering was switched away from HTML parsing, deploy scripts now reject unknown SSH host keys, raw exception details were reduced in key client/webhook paths, FastAPI/Starlette were upgraded to FastAPI `0.136.3` with Starlette `1.0.1`, Shopify/courier webhook authentication now prefers headers or bearer tokens over legacy query secrets, the admin portal moved away from browser `sessionStorage` JWT storage to an HttpOnly cookie session flow with signed CSRF checks for cookie-authenticated admin mutations, and app-level CSP/security headers were added. The exposed server credential must still be rotated outside this repository.

## Verification Performed

- Python tests: `146 passed in 9.55s`.
- WordPress PHP syntax lint: all plugin PHP files passed.
- Admin portal JavaScript syntax: `node --check admin-portal/app.js` passed.
- Client portal TypeScript/lint: `npm run lint` passed.
- Client portal production dependency audit: `npm audit --omit=dev --audit-level=moderate` found 0 vulnerabilities.
- Python dependency audit gap: `python -m pip_audit -r requirements.txt` could not run because `pip_audit` is not installed.
- Installed dependency spot check: FastAPI `0.115.5`, Starlette `0.41.3`, Uvicorn `0.32.1`, python-multipart `0.0.20`, Pydantic `2.10.4`.
- Current advisory spot check: Starlette versions before `0.49.1` are reported vulnerable to FileResponse Range-header DoS, and newer 2026 advisories report Host-header/path issues before `1.0.1`. This project uses both `StaticFiles` and `FileResponse`, so the dependency needs a compatibility-tested upgrade path.

## Critical Findings

### C-1. Hardcoded Live Server Credential

Location: `.cursorrules:41-48`

Evidence: the file contains the production DigitalOcean host, root user, and a literal SSH password/export command. The secret is not repeated in this report.

Risk: anyone with repo/workspace/history access could access the server. Because the secret has already appeared in local project context, assume it is compromised.

Recommended fix:

- Rotate the server password immediately.
- Disable SSH password login and root login.
- Use a least-privilege deploy user with SSH key auth only.
- Remove the secret from `.cursorrules` and purge it from git/history/backups if it was committed.
- Move deploy credentials into a password manager or CI secret store.

## High Findings

### H-1. Admin Password Verification Allows Plaintext Or Unsalted SHA256

Locations:

- `app/routers/admin_api.py:1123-1135`
- `app/routers/admin_views.py:51-65`
- Existing stronger pattern: `app/services/auth_service.py:16-37`

Evidence: admin authentication accepts either `ADMIN_PASSWORD=sha256:<digest>` or a raw plaintext env value. The SHA256 mode is unsalted and fast, so leaked hashes are easier to crack.

Risk: admin account compromise becomes much easier if environment variables, logs, deploy files, or backups leak.

Recommended fix:

- Remove plaintext fallback.
- Replace `sha256:` with PBKDF2/Argon2/bcrypt.
- Add a one-time migration helper that prints a compatible admin password hash.
- Consider separating the CSRF signing secret from `ADMIN_PASSWORD` in `admin_views.py:75-103`.

### H-2. Starlette Was Below Current Security Baselines While Serving Files

Locations:

- `requirements.txt`
- `app/main.py:172-176`
- `app/routers/plugin.py:612-616`

Evidence at audit time: installed Starlette was `0.41.3`; the app mounts `StaticFiles` and returns plugin ZIPs through `FileResponse`.

Risk: Starlette FileResponse/static-file advisories can become unauthenticated CPU or request-routing denial-of-service issues against public endpoints.

Status 2026-06-04: patched in `requirements.txt` to FastAPI `0.136.3` and Starlette `1.0.1`. Local install succeeded, `python -m pip check` passed, and `python -m pytest -q` passed with `148` tests.

Status 2026-06-04: the app-wide `ORJSONResponse` default response class was removed after the FastAPI upgrade, and the now-unused direct `orjson` dependency was removed from `requirements.txt`.

Recommended follow-up:

- Keep `requirements.txt` deployed promptly so production no longer runs Starlette `0.41.3`.

References:

- NVD CVE-2025-62727: https://nvd.nist.gov/vuln/detail/CVE-2025-62727
- GitLab advisory CVE-2025-62727: https://advisories.gitlab.com/pkg/pypi/starlette/CVE-2025-62727/
- NVD CVE-2026-48710: https://nvd.nist.gov/vuln/detail/CVE-2026-48710

### H-3. Deploy Scripts Previously Auto-Trusted SSH Host Keys And Defaulted To Root

Locations:

- `deploy/changed_deploy.py:164-166`
- `deploy/changed_deploy.py:193-202`
- `scripts/ops/deploy_optimized_assets.py:82-91`

Evidence at audit time: deploy code auto-trusted unknown SSH host keys and defaulted to production host/root-style deployment values.

Risk: first-connection MITM attacks are possible, and root deploy access increases blast radius.

Status 2026-06-04: patched to require explicit `DO_SSH_HOST`/`DO_SSH_USER`, reject root/password deploys by default, load a pinned known-hosts file, and use `RejectPolicy()`.

Recommended operational follow-up:

- Use a dedicated deploy user with limited sudo.
- Use SSH keys only; remove password deploy flows.

## Medium Findings

### M-1. Plugin Connect Cancel Flow Allows Open Redirect

Location: `client-portal/src/components/PluginConnectAuthorizeView.tsx:54-63`

Evidence: the cancel flow redirects to `returnUrl` after appending status parameters, while the approve path relies on backend validation.

Risk: a crafted portal authorization URL can send users to an attacker-controlled page when they click Cancel.

Recommended fix: validate cancel redirects with the same host/scheme rules as the backend helper in `app/utils/plugin_connect.py:56-66`, or make the backend return a prevalidated cancel URL.

### M-2. Large Body Limit Can Enable Event Endpoint DoS

Locations:

- `deploy/nginx.conf:80-81`
- `app/routers/tracker.py:214-221`
- `app/routers/events.py:241-247`

Evidence: nginx allows `100M` request bodies; tracker/event endpoints parse JSON/body before all app-level count checks complete.

Risk: public tracking endpoints can be abused for memory/CPU pressure.

Recommended fix:

- Add small route-specific nginx limits for tracking/event routes, for example 256 KB to 1 MB depending on payload needs.
- Reject oversized requests early using `Content-Length`.
- Keep event batch limits before expensive validation where possible.

### M-3. Webhook And Courier Secrets Are Accepted In URLs

Locations:

- `app/routers/webhook.py:231-237`
- `app/routers/courier_webhook.py:142-152`
- `app/routers/courier_webhook.py:572-576`

Evidence at audit time: Shopify and courier webhook helpers accepted API keys/secrets/tokens in query parameters.

Risk: URL secrets leak through reverse-proxy logs, app logs, analytics, browser history, and referrers.

Status 2026-06-04: patched Shopify and courier helpers to prefer `X-API-Key`, provider webhook secret headers, or `Authorization: Bearer`. Query-string keys/tokens remain only as a legacy fallback and now emit deprecation warnings.

Recommended follow-up: update customer/provider setup docs to use headers where the provider supports them, then set a future removal date for query-token fallback.

### M-4. Raw Exception Details Are Returned To Clients

Locations:

- `app/routers/webhook.py:187-190`
- `app/routers/webhook.py:203-208`
- `app/routers/webhook.py:322-325`
- `app/routers/webhook.py:340-343`
- `app/routers/deferred_events.py:175`
- `app/routers/deferred_events.py:317-320`
- `app/routers/client_api.py:1571`
- `app/routers/client_api.py:1587`
- `app/routers/client_api.py:1600`
- `app/routers/client_api.py:1614`

Evidence: API responses include `str(e)` or DB commit exception text.

Risk: clients can see internal schema, provider errors, SQL/driver messages, or operational details.

Recommended fix: return a generic message with a correlation/request id and log the full exception server-side.

### M-5. WordPress Admin UI Inserts AJAX Response Text With innerHTML

Location: `wordpress-plugin/buykori-adsync/includes/admin-settings.php:1411-1419,1459-1467`

Evidence: admin JavaScript builds status messages with `innerHTML` and appends `data.data` or error text.

Risk: admin-side XSS if a remote response or error message contains HTML. The endpoints are nonce/capability protected, but the browser sink is still unsafe.

Recommended fix: use `textContent` or explicit text nodes for response text.

### M-6. Admin JWT Was Stored In Browser sessionStorage

Location: `admin-portal/app.js:35,78`

Evidence at audit time: the admin JWT was read from and written to `sessionStorage`.

Risk: any admin-portal XSS can steal the admin token.

Status 2026-06-04: patched admin login to set an HttpOnly cookie and a signed readable CSRF cookie. Cookie-authenticated admin mutations now require `X-Admin-CSRF-Token`; header/API-key and bearer authentication remain supported for operational scripts.

Status 2026-06-04: app-level CSP/security headers were added, including `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Cross-Origin-Opener-Policy`, and HSTS. Current CSP remains compatibility-safe because legacy marketing/admin templates still use inline scripts/styles.

Status 2026-06-04: the shared admin base template script was moved to `/static/js/admin.js`, and toast styling was moved into `admin.css`. Admin child templates still contain inline event handlers/styles, so removing `'unsafe-inline'` globally is not safe yet.

Status 2026-06-04: `admin/clients.html` no longer emits inline JavaScript handlers for client actions. Copy buttons now use `data-copy-target`, destructive/plan forms use `data-confirm`, and the shared admin script handles those interactions centrally.

Status 2026-06-04: `admin/instructions.html` no longer emits its page-level inline script or inline JavaScript handlers. Tab switching and the JS snippet generator moved to `/static/js/admin-instructions.js`; copy/reveal controls now use data attributes handled by shared admin scripts.

Status 2026-06-04: `admin/dashboard.html` no longer emits inline JavaScript handlers for client-row edit navigation. The edit action is now a normal link, and tests render a real dashboard client to guard against handler regressions.

Status 2026-06-04: `admin/logs.html` and `admin/settings.html` no longer emit inline JavaScript handlers. Refresh and save-feedback actions now use shared data attributes handled by `/static/js/admin.js`.

Status 2026-06-04: `admin/edit.html` was checked and has no inline JavaScript handlers or page-level script. Tests now guard that it remains free of inline script/handler output.

Status 2026-06-04: `admin/edit.html` inline styles were moved into reusable admin CSS utilities (`card-body`, `form-grid-wide`, `section-title`, checkbox labels, warning hints, and form actions). Tests now guard that the edit page emits no `style=` attributes.

Status 2026-06-04: `admin/clients.html` inline visual styles were moved into reusable admin CSS utilities for metrics, client details, plan controls, usage bars, quotas, action rows, and empty states. Monthly usage bar width now hydrates from a data attribute in `/static/js/admin.js`; tests guard that the template stays free of inline `style=` attributes.

Status 2026-06-04: shared admin `base.html`, `admin/logs.html`, and `admin/settings.html` inline visual styles were moved into reusable CSS utilities. Tests now guard that these rendered pages and source templates remain free of inline `style=` attributes.

Status 2026-06-04: `admin/instructions.html` inline visual styles were moved into reusable admin CSS classes for credential cards, tabs, code-copy blocks, alerts, lists, and custom integration summaries. Tests now guard that the rendered instructions page and source template remain free of inline `style=` attributes.

Status 2026-06-04: `admin/dashboard.html` inline visual styles were moved into reusable admin CSS utilities for metrics, tables, alerts, connection status, and forms. Tests now guard that the rendered dashboard and source template remain free of inline `style=` attributes.

Status 2026-06-04: WordPress plugin `includes/admin-settings.php` no longer emits inline event handlers, inline page scripts, `wp_localize_script` inline config, or inline `style=` attributes. The settings page now enqueues `/assets/js/admin-settings.js`, and nonce/ajax config is read from safe `data-*` attributes on the page wrapper.

Status 2026-06-04: WordPress plugin `includes/woo-order-hooks.php` order tracking meta box no longer emits inline styles, inline retry scripts, or `onclick` handlers. Manual retry now uses `/assets/js/admin-order.js`; meta box status styling moved to `/assets/css/admin-order.css`; per-order nonce and order id are carried through button `data-*` attributes.

Status 2026-06-04: WordPress plugin `includes/custom-events.php` no longer emits inline admin builder scripts/styles or generated inline handlers. The builder UI moved to `/assets/js/custom-events-admin.js` and `/assets/css/custom-events-admin.css`; frontend custom event firing moved to `/assets/js/custom-events-tracker.js` with active event definitions carried in a hidden `data-events` element.

Status 2026-06-04: WordPress plugin `includes/dashboard-widget.php` no longer emits inline dashboard widget styles, page scripts, or generated inline style fragments. Widget styling moved to `/assets/css/dashboard-widget.css`; AJAX rendering moved to `/assets/js/dashboard-widget.js`; the widget nonce is passed through a wrapper `data-*` attribute.

Status 2026-06-04: WordPress plugin frontend tracking config no longer emits an inline `window.buykorigw_config` script or manually echoed tracker script tag. `includes/frontend-tracking.php` now enqueues `/assets/js/tracker.js` through WordPress and exposes config through a hidden `data-config` element; `tracker.js` and `custom-events-tracker.js` read that config directly. The remaining settings page `<style>` block was also moved to `/assets/css/admin-settings.css`, leaving the scanned plugin includes/assets free of inline scripts, inline styles, inline handlers, and `wp_localize_script` config.

Recommended follow-up: refactor legacy inline scripts/styles into static assets and move toward nonce/hash-based CSP without `'unsafe-inline'`.

### M-7. Security Headers Are Incomplete

Location: `deploy/nginx.conf:39-42`

Evidence: nginx sets HSTS, `X-Content-Type-Options`, and `X-Frame-Options`, but no Content-Security-Policy, Referrer-Policy, or Permissions-Policy is visible.

Risk: XSS impact and data leakage through referrers are higher than necessary.

Recommended fix:

- Add a conservative CSP per portal/app route.
- Add `Referrer-Policy: strict-origin-when-cross-origin`.
- Add a minimal `Permissions-Policy`.
- Prefer CSP `frame-ancestors` over only `X-Frame-Options`.

### M-8. Public WordPress REST Tracking Endpoints Have Residual Abuse Risk

Locations:

- `wordpress-plugin/buykori-adsync/buykori-adsync.php:950-972`
- `wordpress-plugin/buykori-adsync/buykori-adsync.php:1087-1109`
- `wordpress-plugin/buykori-adsync/buykori-adsync.php:1149-1189`

Evidence: tracking endpoints intentionally use `permission_callback => '__return_true'`. Same-origin checks and rate limiting exist, and nonce is required only when both Origin and Referer are absent.

Risk: this is acceptable for cached storefront tracking, but same-site script/plugin compromise can still generate quota noise or event pollution.

Recommended fix: keep current origin/rate controls, and consider a short-lived storefront signature generated by the plugin for higher-value events.

## Low / Operational Findings

### L-1. Ops Scripts Print Secrets

Locations:

- `deploy/setup.sh:122-135`
- `deploy/setup.sh:141`
- `deploy/setup.sh:159-161`
- `deploy/setup.sh:295-296`
- `scripts/db/check_clients.py:12`
- `scripts/testing/test_event_script.py:19`
- `scripts/ops/tiktok_diag.py:31`

Risk: passwords/API keys can leak into terminal scrollback, CI logs, support screenshots, or shared consoles.

Recommended fix: mask secret output, print only last four characters, or write one-time credentials into protected files.

### L-2. Dirty Worktree And Generated Files Can Cause Deploy Drift

Evidence: the working tree contains many changed/untracked/generated files. Some ignored cache folders also denied permission during status scanning.

Risk: production deploys can accidentally miss needed code or include stale artifacts if deployment is not based on an explicit manifest/commit.

Recommended fix: commit or explicitly document intended deploy files before production deploy. Keep generated caches out of deploy packages.

### L-3. Python Dependency Audit Tool Is Missing

Evidence: `python -m pip_audit -r requirements.txt` failed because `pip_audit` is not installed.

Risk: dependency vulnerabilities may be missed between manual checks.

Recommended fix: add `pip-audit` or `uv pip audit`/`safety` into CI and run it before production deploys.

## Positive Controls Confirmed

- `app/security.py:20-26` requires a valid `ENCRYPTION_KEY`.
- `app/security.py:39-44` disables legacy plaintext decrypt fallback in production.
- `app/main.py:159-166` disables docs unless explicitly enabled.
- `app/main.py:179-182` enables TrustedHost middleware.
- `app/main.py:232-304` separates tracker CORS from credentialed portal CORS.
- `app/routers/client_auth.py:142-154` sets HttpOnly/Secure/SameSite client cookies.
- `app/dependencies.py:71-84` enforces origin checks for cookie-authenticated non-GET requests.
- `app/routers/events.py:253-323` validates signed domain proof when configured.
- `app/routers/events.py:325-334` validates site binding and rate limits.
- `wordpress-plugin/buykori-adsync/includes/auto-updater.php:166-193` verifies update metadata/package integrity.
- WordPress admin AJAX endpoints generally use nonce and capability checks.

## Recommended Fix Order

1. Rotate/remove the hardcoded server credential and harden SSH access.
2. Replace admin password hashing/verification with a slow salted hash and remove plaintext fallback.
3. Upgrade FastAPI/Starlette through a tested compatibility path; add temporary Range-header mitigation if needed.
4. Harden deploy scripts with pinned host keys and a least-privilege deploy user.
5. Add route-specific body limits for public tracking/event endpoints.
6. Fix plugin connect cancel redirect validation.
7. Stop returning raw exception details to clients.
8. Move URL secrets to signed headers/HMAC.
9. Replace WordPress admin `innerHTML` response sinks with safe text rendering.
10. Add CSP/Referrer-Policy/Permissions-Policy and plan an HttpOnly-cookie admin session.
11. Mask secrets in ops scripts.
12. Add Python dependency auditing to CI.
