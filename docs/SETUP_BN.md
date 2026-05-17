# CAPI Gateway সেটআপ গাইড

## WordPress Plugin

1. `wordpress-plugin/capi-gateway.zip` ইনস্টল করুন।
2. WordPress Admin থেকে CAPI Gateway settings খুলুন।
3. Gateway URL দিন।
4. Server API Key দিন।
5. Test Connection চালান।
6. প্রয়োজনীয় event toggle চালু রাখুন।
7. COD হলে Deferred Purchase চালু করুন।

## Client Portal

- Client Portal login-এর জন্য Portal Login Key ব্যবহার করুন।
- Server API Key শুধু plugin, GTM server, বা backend integration-এ ব্যবহার করুন।
- Public tracker key শুধু browser tracker script URL-এ ব্যবহার হবে।

## Server-to-Server Event

Domain lock চালু থাকলে request header-এ এগুলো দিন:

```text
X-API-Key: <server-api-key>
X-CAPI-Origin: https://your-domain.com
```

## Update

- নতুন release দেওয়ার আগে staging site-এ plugin update test করুন।
- Plugin zip rebuild করার পর server update-check endpoint hash/signature দিচ্ছে কি না দেখুন।
