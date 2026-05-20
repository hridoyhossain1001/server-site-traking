# Buykori AdSync Setup Guide

## WordPress Plugin

1. Install `wordpress-plugin/buykori-adsync.zip`.
2. Open Buykori AdSync settings in WordPress Admin.
3. Set the AdSync API URL.
4. Set the Server API Key.
5. Run Test Connection.
6. Enable the event toggles you need.
7. Enable Deferred Purchase for COD workflows.

## Client Portal

- Use the Portal Login Key for client portal access.
- Use the Server API Key only for plugin, GTM server, or backend integrations.
- Use the Public Tracker Key only in browser tracker script URLs.

## Server-to-Server Events

When domain locking is enabled, send:

```text
X-API-Key: <server-api-key>
X-CAPI-Origin: https://your-domain.com
```

## Updates

- Test plugin updates on staging before production.
- After rebuilding the plugin zip, confirm the update-check endpoint returns the expected hash and signature.
