from prometheus_client import Counter, Histogram

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "مدت زمان پردازش هر درخواست HTTP",
    labelnames=["method", "path", "status_code"],
)

reservation_conflicts_total = Counter(
    "reservation_conflicts_total",
    "تعداد کل خطاهای Conflict در رزرو",
)