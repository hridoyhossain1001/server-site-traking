# package init — সব মডেল ইম্পোর্ট করো যেন create_all() কাজ করে
from app.models.client import Client  # noqa: F401
from app.models.event_dedup import EventDedup  # noqa: F401
from app.models.event_log import EventLog  # noqa: F401
from app.models.failed_event import FailedEvent  # noqa: F401
