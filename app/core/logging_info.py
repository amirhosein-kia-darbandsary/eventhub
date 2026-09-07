import logging

import structlog


def configure_logging(json_logs: bool = True) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    renderer = structlog.processors.JSONRenderer(
    ) if json_logs else structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
