import pytest

from app.services import courier_service
from app.services.courier_service import CourierService


class FakeResponse:
    status_code = 200

    def json(self):
        return {
            "status": 200,
            "message": "Consignment has been created successfully.",
            "consignment": {
                "consignment_id": 1424107,
                "tracking_code": "15BAEB8A",
            },
        }


class FakeHttpClient:
    def __init__(self):
        self.request = None

    async def post(self, url, json, headers):
        self.request = {"url": url, "json": json, "headers": headers}
        return FakeResponse()


@pytest.mark.asyncio
async def test_send_to_steadfast_uses_documented_response_and_phone_format(monkeypatch):
    http = FakeHttpClient()

    async def fake_get_http_client():
        return http

    monkeypatch.setattr(courier_service, "get_http_client", fake_get_http_client)

    result = await CourierService.send_to_steadfast(
        api_key="api-key",
        secret_key="secret-key",
        recipient_name="Customer",
        recipient_phone="+8801837224409",
        recipient_address="Dhaka",
        cod_amount=15,
        merchant_order_id="8927",
    )

    assert result["success"] is True
    assert result["courier_order_id"] == "1424107"
    assert result["tracking_id"] == "15BAEB8A"
    assert http.request["json"]["recipient_phone"] == "01837224409"


@pytest.mark.asyncio
async def test_check_steadfast_status_uses_delivery_status_field(monkeypatch):
    class FakeStatusResponse:
        status_code = 200

        def json(self):
            return {"status": 200, "delivery_status": "in_review"}

    class FakeStatusHttpClient:
        async def get(self, url, headers):
            return FakeStatusResponse()

    async def fake_get_http_client():
        return FakeStatusHttpClient()

    monkeypatch.setattr(courier_service, "get_http_client", fake_get_http_client)

    status = await CourierService.check_steadfast_status(
        api_key="api-key",
        secret_key="secret-key",
        tracking_code="15BAEB8A",
    )

    assert status == "in_review"
