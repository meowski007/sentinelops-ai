import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """
    Structured JSON formatter for production-ready IT operations observability.
    Produces parseable log records with timestamps, log levels, and optional metadata.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "incident_id"):
            log_obj["incident_id"] = record.incident_id
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)

    # Use human-friendly format in local dev if preferred, or structured JSON
    if settings.ENVIRONMENT == "production":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Replace existing handlers to avoid duplicates
    root_logger.handlers = [handler]

logger = logging.getLogger("sentinelops")
