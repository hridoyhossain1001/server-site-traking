from locust import HttpUser, between, task
import hashlib
import hmac
import json
import os
import random
import time


class CapiLoadTest(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise RuntimeError("API_KEY env var is required")

        # Optional. Use this when the client has domain lock enabled.
        # Example: CAPI_ORIGIN=https://yourdomain.com
        self.capi_origin = os.getenv("CAPI_ORIGIN", "").strip()

        self.base_headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _headers_for_body(self, body: str) -> dict:
        headers = dict(self.base_headers)
        if self.capi_origin:
            timestamp = str(int(time.time()))
            signature = hmac.new(
                self.api_key.encode("utf-8"),
                f"{timestamp}.{body}".encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            headers.update(
                {
                    "X-CAPI-Origin": self.capi_origin,
                    "X-CAPI-Timestamp": timestamp,
                    "X-CAPI-Signature": signature,
                }
            )
        return headers

    def _post_events(self, payload: dict):
        body = json.dumps({"data": [payload]}, separators=(",", ":"))
        with self.client.post(
            "/api/v1/events",
            data=body,
            headers=self._headers_for_body(body),
            catch_response=True,
        ) as response:
            if response.status_code in (200, 202):
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}: {response.text[:300]}")

    @task(3)
    def send_pageview_event(self):
        now_ms = int(time.time() * 1000)
        payload = {
            "event_name": "PageView",
            "event_time": int(time.time()),
            "event_id": f"load_PageView_{now_ms}_{random.randint(1000, 9999)}",
            "event_source_url": self.capi_origin or "https://example.com/test-page",
            "action_source": "website",
            "user_data": {
                "client_user_agent": "Mozilla/5.0 (Locust Load Test)",
            },
        }
        self._post_events(payload)

    @task(1)
    def send_purchase_event(self):
        now_ms = int(time.time() * 1000)
        order_id = f"load_order_{now_ms}_{random.randint(1000, 9999)}"
        payload = {
            "event_name": "Purchase",
            "event_time": int(time.time()),
            "event_id": order_id,
            "event_source_url": self.capi_origin or "https://example.com/checkout",
            "action_source": "website",
            "user_data": {
                "em": ["test@example.com"],
                "client_user_agent": "Mozilla/5.0 (Locust Load Test)",
            },
            "custom_data": {
                "value": random.randint(500, 5000),
                "currency": "BDT",
                "content_ids": [f"SKU-{random.randint(100, 999)}"],
                "content_type": "product",
                "order_id": order_id,
                "num_items": 1,
            },
        }
        self._post_events(payload)
