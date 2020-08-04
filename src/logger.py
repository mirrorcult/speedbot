DEFAULT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s %(name)s %(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False
        },
        "bot": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False
        },
        "apihandler": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False
        },
        "run": {
            "handlers": ["console"],
            "level": "DEBUG",  # a little less important
            "propagate": False,
        },
        "player": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        }
    }
}
