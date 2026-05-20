# Deployment Checklist

Use this before every production release.

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
- `ENABLE_DOCS` is not set in production unless you intentionally need docs.
- `PLUGIN_VERSION` matches the plugin header version.
- `PLUGIN_DOWNLOAD_URL` points to the production download endpoint.

## 3. Database

- Run migrations:
  `alembic upgrade head`
- Confirm the latest migrations include:
  `portal_key`
  `audit_logs`

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

- Open `/api/v1/admin`.
- Add or inspect a test client.
- Copy the plugin API key and portal key.
- Test WordPress plugin connection.
- Fire one PageView and one Purchase test event.
- Confirm event logs show success.
