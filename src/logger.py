import platform
import sys

if platform.system() == "Linux":
    LOG_PATH = "/home/cyclowns/speedbot/speedbot.log"
elif platform.system() == "Windows":
    # debug only
    LOG_PATH = "K:\\github.com\\cyclowns\\speedbot\\speedbot.log"

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
        "file": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": LOG_PATH,
        }
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False
        },
        "bot": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        "apihandler": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        "run": {
            "handlers": ["console", "file"],
            "level": "DEBUG",  # a little less important
            "propagate": False,
        },
        "user": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        }
    }
}
