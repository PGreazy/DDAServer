import os
from unittest.mock import patch
from dda.env import set_database_url

def test_set_database_url_assembles_connection_string() -> None:
    mock_environ = {
        "DB_HOST": "localhost",
        "DB_PORT": "6432",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpassword",
        "DB_NAME": "test_db"
    }
    with patch.dict(os.environ, mock_environ, clear=True):
        set_database_url()
        assert os.environ["DATABASE_URL"] == "postgres://testuser:testpassword@localhost:6432/test_db"
