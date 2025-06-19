import os
from enum import Enum


class Env(Enum):
    """
    Small enum dictating whether we are currently
    in either a production or local environment
    """

    PRODUCTION = "PROD"
    LOCAL = "LOCAL"

    @staticmethod
    def get_env() -> "Env":
        """
        Extract an Env instance out of the current run environment

        Returns:
            An Env instance that can be used to make decisions based on the
            current runtime environment.
        """
        env_string = os.environ.get("DJANGO_ENV", None)
        if env_string is None:
            raise ValueError("DJANGO_ENV must be set.")
        return Env(env_string)


def set_database_url() -> None:
    """
    Sets the DATABASE_URL environment variable to the construction
    of a connection string from separated variables if the DATABASE_URL
    variable is not already provided.
    """
    if os.environ.get("DATABASE_URL"):
        return

    db_host = os.environ.get("DB_HOST", "")
    db_port = os.environ.get("DB_PORT", "")
    db_user = os.environ.get("DB_USER", "")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_name = os.environ.get("DB_NAME", "")
    os.environ["DATABASE_URL"] = f"postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
