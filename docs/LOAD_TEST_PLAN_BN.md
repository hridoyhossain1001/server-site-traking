# Buykori Load Test Plan

এই প্ল্যানের লক্ষ্য হলো API ingest, dedup, quota, queue, worker pressure, এবং dashboard latency মাপা। Load test কখনও real client credential দিয়ে শুরু করা যাবে না, কারণ event worker Meta/TikTok-এ live delivery করতে পারে।

## Safe Client Rule

1. Admin portal থেকে dedicated `LoadTest` client/store তৈরি করুন।
2. সেই client-এর domain `loadtest.buykori.local` বা safe demo domain-এ lock করুন।
3. Meta CAPI, TikTok Events, GA4, webhook delivery disabled রাখুন অথবা placeholder credential রাখুন।
4. Production URL hit করার আগে script-এ `--unsafe-production-ok` দিতে হবে। এই flag না দিলে script production run block করবে।
5. Default run-এ Purchase পাঠানো হয় না। Purchase path test করতে হলে আলাদা করে `--include-purchase` দিতে হবে।

## Stage 1: Local Smoke

```powershell
$env:CAPI_LOAD_TEST_API_KEY="LOCAL_OR_TEST_CLIENT_API_KEY"
python scripts\testing\load_test.py --dry-run --origin https://loadtest.buykori.local
python scripts\testing\load_test.py --url http://localhost:8000/api/v1/events --rps 5 --duration 20 --concurrency 5 --origin https://loadtest.buykori.local
```

Expected:

- `202` response mostly
- No platform delivery needed
- p95 latency should stay stable

## Stage 2: Production Safe Baseline

```powershell
$env:CAPI_LOAD_TEST_API_KEY="DEDICATED_LOADTEST_CLIENT_API_KEY"
python scripts\testing\load_test.py --url https://api.buykori.app/api/v1/events --unsafe-production-ok --rps 20 --duration 120 --concurrency 20 --origin https://loadtest.buykori.local --json-output C:\tmp\buykori-load-20rps.json
```

Baseline ladder:

- 20 RPS for 2 minutes
- 50 RPS for 2 minutes
- 80 RPS for 2 minutes
- 120 RPS for 1 minute only if CPU, memory, DB, and worker queue remain healthy

Stop immediately if:

- 5xx > 1%
- p95 latency > 1500 ms for more than 30 seconds
- DB CPU or connection pool is saturated
- event outbox/Redis stream backlog keeps growing after the run stops
- platform delivery logs show real Meta/TikTok calls for the load-test client

## Stage 3: Browser Tracker Path

Use this for custom-coded websites that call `/c?key=PUBLIC_KEY`.

```powershell
$env:CAPI_LOAD_TEST_PUBLIC_KEY="DEDICATED_LOADTEST_PUBLIC_KEY"
python scripts\testing\load_test.py --mode tracker --url https://api.buykori.app/c --unsafe-production-ok --rps 20 --duration 120 --concurrency 20 --origin https://loadtest.buykori.local --json-output C:\tmp\buykori-tracker-20rps.json
```

Expected:

- `200` response mostly
- `events_received` should be close to sent events unless dedup/rate-limit intentionally blocks
- If `EVENT_INGEST_MODE=redis_stream`, worker backlog must drain quickly

## Stage 4: Purchase Path

Run this only after baseline is stable and delivery is disabled on the LoadTest client.

```powershell
python scripts\testing\load_test.py --url https://api.buykori.app/api/v1/events --unsafe-production-ok --include-purchase --rps 10 --duration 60 --concurrency 10 --origin https://loadtest.buykori.local
```

Expected:

- Purchase deferred/queue behavior should match client settings
- No duplicate Purchase IDs
- Pending/incomplete order test data can be cleaned after the run

## What To Record

- request RPS and event RPS
- status count
- accepted events count
- p50, p95, p99 latency
- API CPU/memory
- DB CPU/connections
- worker queue backlog
- event delivery success/failure by platform
- dashboard freshness delay

## Current Harness

`scripts/testing/load_test.py` supports:

- signed `/api/v1/events` route
- public `/c` tracker route
- controlled RPS instead of firing all requests at once
- realistic PageView, ViewContent, AddToCart, InitiateCheckout mix
- optional Purchase mix
- JSON summary output
- production guard flag
