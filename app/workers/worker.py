"""
Put all the workers here for running them easily with just one command

"""
from app.core.setup_dramiq import redis_broker  # noqa: f401
from app.workers.notification_worker import *  # noqa: f401
from app.workers.reservation_cleanup_worker import * # noqa :f401