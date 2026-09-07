import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# --- بخش ۱: structlog -- فقط یک بار در شروع برنامه کانفیگ می‌شه ---
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),  # خروجی نهایی: یک خط JSON
    ]
)
log = structlog.get_logger()

# --- بخش ۲: OpenTelemetry -- یک TracerProvider با یک exporter که فقط
# روی کنسول چاپ می‌کنه (به‌جای فرستادن به Jaeger واقعی) ---
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("throwaway-demo")


def main():
    # یک لاگ ساختاری ساده
    log.info("reservation_created", reservation_id=42, user_id=7, quantity=2)

    # یک span -- یعنی "این بلوک کد از الان تا انتهای with طول کشید"
    with tracer.start_as_current_span("process_reservation") as span:
        span.set_attribute("reservation.id", 42)
        span.set_attribute("reservation.quantity", 2)
        log.info("processing_started", reservation_id=42)
        # ... اینجا کار واقعی انجام می‌شد ...
        log.info("processing_finished", reservation_id=42)


if __name__ == "__main__":
    main()