import os
from locust import HttpUser, task, between
import time

class CapiUser(HttpUser):
    wait_time = between(0.01, 0.1)  # High frequency
    
    def on_start(self):
        self.api_key = os.getenv("CAPI_LOAD_TEST_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set CAPI_LOAD_TEST_API_KEY before running Locust.")
        self.headers = {"X-API-Key": self.api_key}

    @task
    def send_event(self):
        payload = {
            "data": [{
                "event_name": "PageView",
                "event_time": int(time.time()),
                "event_id": f"locust_{time.time_ns()}",
                "event_source_url": "http://example.com/locust-test",
                "user_data": {
                    "client_ip_address": "8.8.8.8",
                    "client_user_agent": "Locust-Load-Tester"
                }
            }],
            "test_event_code": "TEST_LOCUST"
        }
        with self.client.post("/api/v1/events", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 502:
                # 502 is expected for dummy tokens as it enters retry queue
                response.success()
            else:
                response.failure(f"Got status {response.status_code}: {response.text}")
