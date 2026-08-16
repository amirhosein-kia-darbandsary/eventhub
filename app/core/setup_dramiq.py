import dramatiq
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware
from app.core.config import get_settings
import socket

_settings = get_settings()


import socket
redis_broker = RedisBroker(
    url=_settings.redis.url,
    socket_timeout=10,
    socket_connect_timeout=10,
    socket_keepalive=True,
    socket_keepalive_options={
        socket.TCP_KEEPIDLE: 30,   
        socket.TCP_KEEPINTVL: 10, 
        socket.TCP_KEEPCNT: 3,     
    },
)
redis_broker.add_middleware(PeriodiqMiddleware(skip_delay=30))
dramatiq.set_broker(redis_broker)