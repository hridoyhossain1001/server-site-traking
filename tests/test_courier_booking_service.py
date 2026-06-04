from types import SimpleNamespace

import pytest

from app.models.client import Client
from app.models.courier_booking_job import CourierBookingJob
from app.models.courier_order import CourierOrder
from app.models.pending_event import PendingEvent
from app.services import courier_booking_service


class _ScalarResult:
    def __init__(self, value=None, values=None):
        self.value = value
        self.values = values

    def scalar_one_or_none(self):
        return self.value

    def scalars(self):
        return self

    def all(self):
        return list(self.values or [])


class _FakeDb:
    def __init__(self, results=None, objects=None):
        self.results = list(results or [])
        self.objects = dict(objects or {})
        self.added = []
        self.committed = False
        self.rolled_back = False

    async def execute(self, _query):
        return self.results.pop(0)

    async def get(self, model, object_id):
        return self.objects.get((model, object_id))

    def add(self, value):
        self.added.append(value)

    async def flush(self):
        for value in self.added:
            if isinstance(value, CourierOrder) and value.id is None:
                value.id = 55

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


def _client(**overrides):
    values = {
        "id": 7,
        "steadfast_api_key": "steadfast-key",
        "steadfast_secret_key": "encrypted-secret",
        "pathao_api_key": None,
        "pathao_secret_key": None,
        "pathao_store_id": None,
        "redx_access_token": None,
        "redx_delivery_area_id": None,
        "redx_delivery_area_name": None,
        "redx_pickup_store_id": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _pending(**overrides):
    values = {
        "id": 12,
        "order_id": "ORDER-12",
        "raw_order_data": {
            "recipient_name": "Customer",
            "recipient_phone": "01837224409",
            "recipient_address": "Dhaka",
            "cod_amount": 150,
        },
        "event_data": {},
        "status": "pending",
        "portal_state": "pending",
        "is_confirmed": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.asyncio
async def test_enqueue_courier_booking_creates_durable_placeholder():
    db = _FakeDb(results=[_ScalarResult(), _ScalarResult()])
    pending = _pending()

    result = await courier_booking_service.enqueue_courier_booking(
        db,
        client=_client(),
        pending=pending,
        provider="steadfast",
    )

    order = result["courier_order"]
    job = next(value for value in db.added if isinstance(value, CourierBookingJob))
    assert result["mode"] == "queued"
    assert order.id == 55
    assert order.courier_status == "booking_queued"
    assert job.status == "queued"
    assert job.courier_order_id == 55
    assert pending.status == "courier_booking_queued"
    assert pending.is_confirmed is True


@pytest.mark.asyncio
async def test_enqueue_courier_booking_is_idempotent_for_existing_placeholder():
    order = CourierOrder(id=55, client_id=7, order_id="ORDER-12", courier_status="booking_queued")
    db = _FakeDb(results=[_ScalarResult(order)])

    result = await courier_booking_service.enqueue_courier_booking(
        db,
        client=_client(),
        pending=_pending(),
        provider="steadfast",
    )

    assert result["mode"] == "already_booked"
    assert result["courier_order"] is order
    assert db.added == []


@pytest.mark.asyncio
async def test_enqueue_rejects_malformed_pathao_credentials(monkeypatch):
    monkeypatch.setattr(courier_booking_service, "decrypt_token", lambda _value: "missing-separator")

    with pytest.raises(ValueError, match="Pathao credentials format is invalid"):
        await courier_booking_service.enqueue_courier_booking(
            _FakeDb(),
            client=_client(pathao_api_key="missing-separator", pathao_secret_key="encrypted"),
            pending=_pending(),
            provider="pathao",
        )


@pytest.mark.asyncio
async def test_cancel_queued_booking_stops_provider_dispatch():
    pending = _pending(status="courier_booking_queued", portal_state="processing", is_confirmed=True)
    order = CourierOrder(
        id=55,
        client_id=7,
        pending_event_id=pending.id,
        order_id=pending.order_id,
        courier_status="booking_queued",
        status_history=[],
    )
    job = SimpleNamespace(status="queued", locked_at=None, locked_by=None)
    db = _FakeDb(
        results=[_ScalarResult(job)],
        objects={(PendingEvent, pending.id): pending},
    )

    assert await courier_booking_service.cancel_queued_booking(db, order) is True
    assert job.status == "cancelled"
    assert order.courier_status == "cancelled"
    assert pending.status == "cancelled"
    assert pending.portal_state == "cancelled"


@pytest.mark.asyncio
async def test_cancel_rejects_booking_already_claimed_by_worker():
    order = CourierOrder(id=55, client_id=7, order_id="ORDER-12", courier_status="booking_processing")
    db = _FakeDb()

    assert await courier_booking_service.cancel_queued_booking(db, order) is False
    assert db.results == []


@pytest.mark.asyncio
async def test_claim_due_booking_jobs_marks_order_processing():
    job = SimpleNamespace(id=91, courier_order_id=55, status="queued", locked_at=None, locked_by=None)
    order = SimpleNamespace(courier_status="booking_queued")
    db = _FakeDb(
        results=[_ScalarResult(values=[job])],
        objects={(CourierOrder, 55): order},
    )

    ids = await courier_booking_service.claim_due_booking_jobs(db)

    assert ids == [91]
    assert job.status == "processing"
    assert job.locked_by == courier_booking_service.WORKER_ID
    assert order.courier_status == "booking_processing"
    assert db.committed is True


@pytest.mark.asyncio
async def test_claim_due_booking_jobs_claims_each_batch_item_once():
    jobs = [
        SimpleNamespace(id=index, courier_order_id=index + 1000, status="queued", locked_at=None, locked_by=None)
        for index in range(1, 101)
    ]
    orders = {
        (CourierOrder, job.courier_order_id): SimpleNamespace(courier_status="booking_queued")
        for job in jobs
    }
    db = _FakeDb(results=[_ScalarResult(values=jobs)], objects=orders)

    ids = await courier_booking_service.claim_due_booking_jobs(db, limit=100)

    assert ids == list(range(1, 101))
    assert len(set(ids)) == 100
    assert all(job.status == "processing" for job in jobs)
    assert all(job.locked_by == courier_booking_service.WORKER_ID for job in jobs)
    assert all(order.courier_status == "booking_processing" for order in orders.values())
    assert db.committed is True


@pytest.mark.asyncio
async def test_claim_due_booking_jobs_rolls_back_empty_batch():
    db = _FakeDb(results=[_ScalarResult(values=[])])

    assert await courier_booking_service.claim_due_booking_jobs(db) == []
    assert db.rolled_back is True


@pytest.mark.asyncio
async def test_operator_retry_requeues_dead_letter_and_reopens_processing_state():
    pending = _pending(status="pending", portal_state="pending", is_confirmed=False)
    order = CourierOrder(
        id=55,
        client_id=7,
        pending_event_id=pending.id,
        order_id=pending.order_id,
        courier_status="booking_failed",
        status_history=[],
    )
    job = SimpleNamespace(
        id=91,
        status="dead",
        courier_order_id=order.id,
        pending_event_id=pending.id,
        attempts=8,
        max_attempts=8,
        next_attempt_at=None,
        locked_at="locked",
        locked_by="worker",
        sent_at="sent",
        last_error="provider timeout",
    )
    db = _FakeDb(
        results=[_ScalarResult(job)],
        objects={(CourierOrder, order.id): order, (PendingEvent, pending.id): pending},
    )

    result = await courier_booking_service.requeue_failed_booking_job(db, job.id)

    assert result is job
    assert job.status == "queued"
    assert job.attempts == 0
    assert job.next_attempt_at is not None
    assert job.locked_at is None
    assert job.locked_by is None
    assert job.sent_at is None
    assert job.last_error is None
    assert order.courier_status == "booking_queued"
    assert pending.status == "courier_booking_queued"
    assert pending.portal_state == "processing"
    assert pending.is_confirmed is True


@pytest.mark.asyncio
async def test_operator_retry_rejects_processing_job():
    job = SimpleNamespace(id=91, status="processing")
    db = _FakeDb(results=[_ScalarResult(job)])

    with pytest.raises(ValueError, match="Only dead courier booking jobs"):
        await courier_booking_service.requeue_failed_booking_job(db, job.id)


class _SessionFactory:
    def __init__(self, sessions):
        self.sessions = list(sessions)

    def __call__(self):
        session = self.sessions.pop(0)
        return _SessionContext(session)


class _SessionContext:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, *_args):
        return None


@pytest.mark.asyncio
async def test_processing_success_marks_job_sent_and_pending_booked(monkeypatch):
    job = SimpleNamespace(
        id=91,
        status="processing",
        client_id=7,
        courier_order_id=55,
        pending_event_id=12,
        provider="steadfast",
        request_payload={
            "recipient_name": "Customer",
            "recipient_phone": "01837224409",
            "recipient_address": "Dhaka",
            "cod_amount": 150,
        },
        attempts=0,
        max_attempts=3,
        locked_at="locked",
        locked_by="worker",
        next_attempt_at=None,
        last_error="old error",
        sent_at=None,
    )
    order = SimpleNamespace(
        order_id="ORDER-12",
        courier_order_id=None,
        courier_tracking_id=None,
        courier_status="booking_processing",
        status_history=[],
    )
    pending = _pending(status="courier_booking_queued", portal_state="processing", is_confirmed=True)
    client = _client()
    load_db = _FakeDb(objects={(CourierBookingJob, 91): job, (Client, 7): client, (CourierOrder, 55): order})
    success_db = _FakeDb(objects={(CourierBookingJob, 91): job, (CourierOrder, 55): order, (PendingEvent, 12): pending})

    async def provider_success(*_args, **_kwargs):
        return {"success": True, "courier_order_id": "SF-123", "tracking_id": "TRK-123"}

    monkeypatch.setattr(courier_booking_service, "AsyncSessionLocal", _SessionFactory([load_db, success_db]))
    monkeypatch.setattr(courier_booking_service, "_send_to_provider", provider_success)

    await courier_booking_service.process_booking_job(91)

    assert job.status == "sent"
    assert job.sent_at is not None
    assert job.locked_at is None
    assert job.locked_by is None
    assert job.last_error is None
    assert order.courier_order_id == "SF-123"
    assert order.courier_tracking_id == "TRK-123"
    assert order.courier_status == "pending"
    assert pending.status == "courier_booked"
    assert pending.portal_state == "processing"
    assert pending.is_confirmed is True
    assert success_db.committed is True


@pytest.mark.asyncio
async def test_processing_failure_requeues_with_backoff(monkeypatch):
    job = SimpleNamespace(
        id=91,
        status="processing",
        client_id=7,
        courier_order_id=55,
        pending_event_id=12,
        provider="steadfast",
        request_payload={},
        attempts=0,
        max_attempts=3,
        locked_at="locked",
        locked_by="worker",
        next_attempt_at=None,
        last_error=None,
    )
    order = SimpleNamespace(order_id="ORDER-12", courier_status="booking_processing")
    pending = _pending(status="courier_booking_queued", portal_state="processing", is_confirmed=True)
    client = _client()
    load_db = _FakeDb(objects={(CourierBookingJob, 91): job, (Client, 7): client, (CourierOrder, 55): order})
    retry_db = _FakeDb(objects={(CourierBookingJob, 91): job, (CourierOrder, 55): order, (PendingEvent, 12): pending})

    async def fail_provider(*_args, **_kwargs):
        raise RuntimeError("provider timeout")

    monkeypatch.setattr(courier_booking_service, "AsyncSessionLocal", _SessionFactory([load_db, retry_db]))
    monkeypatch.setattr(courier_booking_service, "_send_to_provider", fail_provider)

    await courier_booking_service.process_booking_job(91)

    assert job.status == "queued"
    assert job.attempts == 1
    assert job.last_error == "provider timeout"
    assert job.next_attempt_at is not None
    assert order.courier_status == "booking_queued"
    assert retry_db.committed is True


@pytest.mark.asyncio
async def test_final_processing_failure_dead_letters_and_reopens_pending(monkeypatch):
    job = SimpleNamespace(
        id=91,
        status="processing",
        client_id=7,
        courier_order_id=55,
        pending_event_id=12,
        provider="steadfast",
        request_payload={},
        attempts=2,
        max_attempts=3,
        locked_at="locked",
        locked_by="worker",
        next_attempt_at=None,
        last_error=None,
    )
    order = SimpleNamespace(order_id="ORDER-12", courier_status="booking_processing", status_history=[])
    pending = _pending(status="courier_booking_queued", portal_state="processing", is_confirmed=True)
    client = _client()
    load_db = _FakeDb(objects={(CourierBookingJob, 91): job, (Client, 7): client, (CourierOrder, 55): order})
    retry_db = _FakeDb(objects={(CourierBookingJob, 91): job, (CourierOrder, 55): order, (PendingEvent, 12): pending})

    async def fail_provider(*_args, **_kwargs):
        raise RuntimeError("provider timeout")

    monkeypatch.setattr(courier_booking_service, "AsyncSessionLocal", _SessionFactory([load_db, retry_db]))
    monkeypatch.setattr(courier_booking_service, "_send_to_provider", fail_provider)

    await courier_booking_service.process_booking_job(91)

    assert job.status == "dead"
    assert order.courier_status == "booking_failed"
    assert pending.status == "pending"
    assert pending.portal_state == "pending"
    assert pending.is_confirmed is False
