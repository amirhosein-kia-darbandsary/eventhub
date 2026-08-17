
```shell
eventhub/
├── app/
│   ├── main.py                  # اپ FastAPI + همه‌ی middleware + همه‌ی routerها
│   ├── worker.py                # نقطه‌ی ورود مرکزی Dramatiq -- همه‌ی actorها اینجا import می‌شن
│   ├── core/
│   │   ├── config.py             # Settings (DatabaseSettings, RedisSettings, JWTSettings, CORSSettings, payment_provider_url)
│   │   ├── security.py           # bcrypt (نه passlib!) + JWT RS256
│   │   ├── exceptions.py         # DomainError و زیرکلاس‌هاش (NotFoundError, ConflictError, ValidationAppError, ForbiddenError, InvalidTokenError, InvalidCredentialsError)
│   │   ├── error_handlers.py     # exception handler سراسری برای همه‌ی موارد بالا + RequestValidationError + IntegrityError
│   │   ├── pagination.py         # paginate() عمومی -- cursor-based، کار با هر ستون/نوع
│   │   ├── caching.py            # cache_aside(), invalidate_cache()
│   │   ├── redis_client.py       # redis.asyncio client، decode_responses=True
│   │   ├── dramatiq_setup.py     # RedisBroker + PeriodiqMiddleware، با socket_keepalive تنظیم‌شده
│   │   └── middleware/
│   │       ├── request_id.py     # ASGI خام، بیرونی‌ترین لایه‌ی onion
│   │       ├── timing.py         # BaseHTTPMiddleware، X-Response-Time
│   │       └── rate_limit.py     # in-memory، موقتی (باید بشه Redis-based)
│   ├── db/
│   │   ├── base.py               # Base (DeclarativeBase)
│   │   └── session.py            # get_db, async_session_factory, engine (pool_size=5, max_overflow=10)
│   ├── models/                   # User, Venue, Event, TicketType, Reservation, WebhookEvent
│   ├── schemas/                  # Create/Update/Read برای هر مدل + common.py (ErrorResponse, CursorPage)
│   ├── repositories/
│   │   └── venue_repository.py   # Protocol + SqlAlchemyVenueRepository -- فقط برای منطق واقعی، نه CRUD ساده
│   ├── services/                 # منطق خالص کسب‌وکاری -- بدون وابستگی به HTTP/Dramatiq
│   │   ├── ticket_type_service.py     # calculate_available()
│   │   ├── event_service.py           # validate_venue_exists()
│   │   ├── reservation_service.py     # create_reservation, cancel_reservation, confirm_reservation (عمومی) / confirm_reservation_internal (سیستمی) / _confirm_reservation_core (مشترک)، cleanup_expired_reservations
│   │   ├── notification_service.py    # send_confirmation_email -- منطق خالص، بدون Dramatiq
│   │   ├── payment_service.py         # initiate_payment -- retry (tenacity) + circuit breaker (pybreaker)
│   │   └── payment_webhook_service.py # process_payment_webhook_logic
│   ├── workers/                  # آداپتورهای نازک Dramatiq -- فقط چسب بین صف و service
│   │   ├── notification_worker.py
│   │   ├── reservation_cleanup_worker.py  # periodic با cron("*/5 * * * *")
│   │   └── payment_webhook_worker.py      # با on_retry_exhausted="mark_webhook_as_dead_letter"
│   └── api/                      # routerها -- فقط "چسب" بین HTTP و service
│       ├── auth.py, venues.py, events.py, ticket_types.py, reservations.py, checkout.py, webhooks.py
├── tests/
│   ├── unit/                     # سریع، بدون I/O -- @pytest.mark.unit
│   └── integration/               # با Postgres واقعی -- @pytest.mark.integration
│       └── conftest.py            # db_session (SAVEPOINT rollback), client (httpx.AsyncClient+ASGITransport), admin_client, concurrency_client (NullPool، بدون rollback), concurrency_admin_headers
├── mock-payment-provider/        # پروژه‌ی کاملاً جدا، پورت ۸۲۰۰ -- شبیه‌ساز درگاه پرداخت
├── adr/                          # تصمیمات معماری، شماره‌گذاری‌شده
└── .env, .env.test
```

## اجرای تست‌ها

دو مجموعه‌ی جدا از تست داریم:

- **`pytest -m unit`** — سریع (چند ثانیه)، بدون هیچ وابستگی بیرونی. باید در
  **هر push، روی هر برنچ** اجرا بشه — چون هزینه‌اش تقریباً صفره.
- **`pytest -m integration`** — نیاز به یک Postgres واقعی داره (از طریق
  `.env.test`). کندتره. باید فقط روی **pull requestها به سمت `main`**
  اجرا بشه (نه هر commit)، تا CI رو کند نکنه.

CI (که هنوز نساختیمش) قرار است این دو مرحله رو جدا اجرا کنه:
1. `pytest -m unit` — روی هر push
2. `pytest -m integration` — فقط روی PR، با یک سرویس Postgres که در همون
   pipeline (مثلاً به‌عنوان یک "service container" در GitHub Actions) بالا میاد