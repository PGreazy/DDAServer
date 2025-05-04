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
