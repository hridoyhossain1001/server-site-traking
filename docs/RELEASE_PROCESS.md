# Release Process

Keep the server version, plugin version, zip package, and changelog in sync.

## Version Rules

- WordPress plugin header version in `wordpress-plugin/capi-gateway/capi-gateway.php`.
- `CAPIGW_VERSION` in the same file.
- Server `PLUGIN_VERSION` default in `app/routers/plugin.py`.
- Plugin `readme.txt` changelog.

All four should describe the same release.

## Release Steps

1. Update plugin code.
2. Update server code if needed.
3. Update changelog.
4. Run Python compile checks.
5. Run `pytest`.
6. Run PHP lint for every plugin PHP file.
7. Rebuild `wordpress-plugin/capi-gateway.zip` and `capi-gateway-updated.zip` with `python zip_plugin.py`.
8. Deploy server.
9. Run `alembic upgrade head`.
10. Test update flow in staging.
11. Release to production clients.

## Rollback

- Keep the last known working zip as a backup.
- If the update flow fails, restore the previous zip and version metadata.
- If a database migration causes an issue, stop the app and restore from database backup before retrying.
