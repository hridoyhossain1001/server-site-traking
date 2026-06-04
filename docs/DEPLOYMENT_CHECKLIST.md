# Deployment Checklist

Use this before every production release.

## 0. Select the Exact Component

- Read `docs/REPO_DEPLOYMENT_MATRIX.md`.
- Run:
  `powershell -ExecutionPolicy Bypass -File scripts\ops\deploy_preflight.ps1 -Target all`
- Marketing, client, and admin releases go only to their matching GitHub repository.
- Backend code must not be pushed to GitHub in the approved release flow.
- Backend production deployment requires explicit approval and a reviewed direct server deploy.

## 1. Local Verification

- Run Python syntax checks:
  `python -m py_compile app\main.py app\routers\admin.py app\routers\client_portal.py app\routers\events.py app\routers\plugin.py`
- Run tests:
  `pytest`
- Run PHP lint:
  `php -l wordpress-plugin\buykori-adsync\buykori-adsync.php`
- Lint all plugin PHP files:
  `$files = rg --files wordpress-plugin\buykori-adsync -g '*.php'; foreach ($file in $files) { php -l $file }`

## 2. Environment Variables

- `DATABASE_URL` is set.
- `ENCRYPTION_KEY` is set and unchanged from previous production deploy.
- `ADMIN_USERNAME` is set.
- `ADMIN_PASSWORD` is set.
- `ADMIN_API_KEY` is set.
- Courier booking queue worker settings are present or intentionally using defaults:
  `COURIER_BOOKING_WORKER_BATCH_SIZE`
  `COURIER_BOOKING_WORKER_POLL_SECONDS`
  `COURIER_BOOKING_STALE_LOCK_SECONDS`
  `COURIER_BOOKING_MAX_ATTEMPTS`
  `COURIER_BOOKING_QUEUE_WARN_SECONDS`
  `COURIER_BOOKING_PROCESSING_WARN_SECONDS`
- `ENABLE_DOCS` is not set in production unless you intentionally need docs.
- `PLUGIN_VERSION` matches the plugin header version.
- `PLUGIN_DOWNLOAD_URL` points to the production download endpoint.
- `PLUGIN_PROTECTED_PACKAGE=true` keeps shipped plugin ZIPs less self-explanatory while preserving WordPress metadata.
- `PLUGIN_PRECONFIGURED_DOWNLOADS=false` keeps plugin downloads generic; WordPress connects through account authorization.
- `GEOIP_ENRICH_IN_REQUEST=false` and `TRACKER_ENRICH_IN_REQUEST=false` keep ingest requests light; the event worker enriches queued events.

## 3. Database

- Run migrations:
  `alembic upgrade head`
- Confirm migration head:
  `alembic heads`
- Confirm the latest migrations include:
  `portal_key`
  `audit_logs`
  `courier_booking_jobs`

## 4. Plugin Package

- Rebuild plugin zip:
  `python zip_plugin.py`
- Confirm zip contains `buykori-adsync/` as the root folder.
- Confirm server update metadata returns:
  `version`
  `download_url`
  `package_sha256`
  `signature`

## 5. Smoke Test

- Run read-only backend smoke checks:
  `python scripts\ops\staging_smoke_check.py --base-url https://api.buykori.app --admin-api-key <ADMIN_API_KEY>`
- Open `/api/v1/admin`.
- Add or inspect a test client.
- Copy the plugin API key and portal key.
- Test WordPress plugin connection.
- Fire one PageView and one Purchase test event.
- Confirm event logs show success.
- Open the admin portal Courier Queue tab.
- Confirm `/api/v1/admin/api/summary` shows `courier_booking_queue`.
- Confirm `/api/v1/admin/api/courier-booking-queue?limit=20` returns queue metrics and recent jobs.
- Queue one courier booking from a test order and confirm it moves from `queued` to `sent`.
- If a job is `dead`, confirm the Retry action requeues it and the alert clears after successful processing.
