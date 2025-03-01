import enum
import os

SECRET_KEY = os.environ["DJANGO_SECRET"]
DEBUG = os.environ.get("DEBUG", None) == "True"
ROOT_URLCONF = "dda.urls"


class Env(enum.Enum):
    PRODUCTION = "PROD"
    LOCAL = "LOCAL"


ENVIRONMENT = Env(os.environ.get("DJANGO_ENV", "LOCAL"))


def get_log_level() -> str:
    if ENVIRONMENT == Env.LOCAL or DEBUG:
        return "DEBUG"
    return "INFO"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "basic": {
            "format": "[{asctime}] level={levelname} tid={tid} user_id={user_id} message={message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": get_log_level(),
            "class": "logging.StreamHandler",
            "formatter": "basic",
        }
    },
    "loggers": {
        "dda": {
            "handlers": ["console"],
            "level": get_log_level(),
            "propagate": True,
        }
    },
}


MIDDLEWARE = [
    "dda.v1.routes.middleware.transaction.transaction_middleware"
]
