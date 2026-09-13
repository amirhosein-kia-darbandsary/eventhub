from prometheus_client import Counter, Histogram, Gauge

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "مدت زمان پردازش هر درخواست HTTP",
    labelnames=["method", "path", "status_code"],
)

reservation_conflicts_total = Counter(
    "reservation_conflicts_total",
    "تعداد کل خطاهای Conflict در رزرو",
)


db_pool_checked_out = Gauge(
    "db_pool_checked_out",
    "تعداد connectionهای دیتابیس که همین الان در حال استفاده‌ان",
)

db_pool_size = Gauge(
    "db_pool_size",
    "حداکثر ظرفیت pool (pool_size + max_overflow)",
)
