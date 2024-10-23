import os
import socket
import logging
from datetime import datetime, timezone

from pythonjsonlogger import jsonlogger


class AWSCustomJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self, *args, **kwargs):
        super(AWSCustomJsonFormatter, self).__init__(*args, **kwargs)
        self.product_name = os.environ.get("TS_LOG_PRODUCT_NAME", "intelligence-portal")
        self.service_name = os.environ.get("TS_LOG_SERVICE_NAME", "partner-creation")
        self.hostname = socket.gethostname()
        self.region = os.environ.get("AWS_REGION") or os.environ.get(
            "AWS_DEFAULT_REGION", "us-east-1"
        )

    def add_fields(self, log_record, record, message_dict):
        super(AWSCustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # Add mandatory fields with UTC timestamp
        log_record["ts_timestamp"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        log_record["ts_product"] = self.product_name
        log_record["ts_service"] = self.service_name
        log_record["ts_region"] = self.region
        log_record["ts_hostname"] = self.hostname

        # Add other standard fields
        log_record["levelname"] = record.levelname
        log_record["name"] = record.name


def get_basic_json_logger(name, level="INFO"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Disable propagation to prevent duplicate logs
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = AWSCustomJsonFormatter(
        fmt="%(ts_timestamp)s %(ts_product)s %(ts_service)s %(ts_region)s %(ts_hostname)s %(levelname)s %(name)s %(filename)s %(funcName)s %(lineno)d %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def setup_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Disable propagation to prevent duplicate logs
    logger.propagate = False

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    handler = logging.StreamHandler()
    formatter = AWSCustomJsonFormatter(
        fmt="%(ts_timestamp)s %(ts_product)s %(ts_service)s %(ts_region)s %(ts_hostname)s %(levelname)s %(name)s %(filename)s %(funcName)s %(lineno)d %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_uvicorn_log_config(level):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "app.core.logging.AWSCustomJsonFormatter",
                "fmt": "%(ts_timestamp)s %(ts_product)s %(ts_service)s %(ts_region)s %(ts_hostname)s %(levelname)s %(name)s %(filename)s %(funcName)s %(lineno)d %(message)s",
            }
        },
        "handlers": {
            "default": {
                "formatter": "json",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            }
        },
        "loggers": {
            "": {"handlers": ["default"], "level": level},
            "uvicorn": {"handlers": ["default"], "level": level, "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": level},
            "uvicorn.access": {
                "handlers": ["default"],
                "level": level,
                "propagate": False,
            },
            "fastapi": {"handlers": ["default"], "level": level, "propagate": False},
        },
    }