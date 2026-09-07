"""
Put all the workers here for running them easily with just one command

"""
from app.core.logging_info import configure_logging
from app.core.config import get_settings
configure_logging(json_logs=not get_settings().debug)

from app.core.setup_dramiq import redis_broker  # noqa: f401
from app.workers.notification_worker import *  # noqa: f401
from app.workers.reservation_cleanup_worker import *  # noqa :f401
from app.workers.payment_service_worker import process_payment_webhook, mark_webhook_as_dead_letter  # noqa: F401
from app.models import event, reserve, ticket_type, user, venue, webhook  # noqa: F401
