import json, logging, sys, contextvars
from datetime import datetime, timezone
from typing import Optional, Dict, Any

correlation_id_ctx = contextvars.ContextVar("correlation_id", default="system")
user_id_ctx = contextvars.ContextVar("user_id", default=None)
device_id_ctx = contextvars.ContextVar("device_id", default=None)

def set_correlation_id(corr_id: str): correlation_id_ctx.set(corr_id)
def get_correlation_id() -> str: return correlation_id_ctx.get()
def set_user_id(uid: Optional[str]): user_id_ctx.set(uid)
def get_user_id() -> Optional[str]: return user_id_ctx.get()
def set_device_id(did: Optional[str]): device_id_ctx.set(did)
def get_device_id() -> Optional[str]: return device_id_ctx.get()

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "chatbot-service"),
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
            "user_id": get_user_id(),
            "device_id": get_device_id(),
            "path": f"{record.filename}:{record.lineno}",
            "process": record.process,
            "thread": record.threadName
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def get_logger(name: str = "chatbot-core", service: str = "chatbot-service") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
