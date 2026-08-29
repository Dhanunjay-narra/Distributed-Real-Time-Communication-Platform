import json, logging, sys
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Optional, Dict, Any

correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)

def set_correlation_id(correlation_id: str) -> None: correlation_id_ctx.set(correlation_id)
def get_correlation_id() -> Optional[str]: return correlation_id_ctx.get()
def set_user_id(user_id: str) -> None: user_id_ctx.set(user_id)

class JSONFormatter(logging.Formatter):
    def __init__(self, service_name: str = "chatbot-service"):
        super().__init__()
        self.service_name = service_name
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get() or "system",
            "user_id": user_id_ctx.get(),
            "path": f"{record.filename}:{record.lineno}",
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def get_logger(name: str, service_name: str = "chatbot-service") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(JSONFormatter(service_name=service_name))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger
