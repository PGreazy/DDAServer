# DDA Server
This repository contains the backend components of DDA (someday we'll have a proper name).
This includes everything from users to characters to campaigns, monoliths FTW.

# Environment Setup
To begin running the service, do the following:
1. Install poetry.
2. Install Postgres, and create a local database. Feel free to create user credentials named as you see fit, same for the database. No assumptions are made in code.
3. Grab an IDE of your choice. We officially support PyCharm with run configurations.
4. Install pre-commit, and install the precommit hooks with `pre-commit install`.

# Running Locally
The project is configured to use in-project virtual environments
by default, for the sake of simplicity. Once poetry is installed, install dependencies:
```commandline
poetry install --with dev,test
```
With all dependencies installed, you should be able to run the database
migrations (ensure you have a local Postgres instance setup, and have set the environment
variable DATABASE_URL accordingly):
```commandline
python manage.py migrate
```
And now, you can finally start the service!
```commandline
python -m uvicorn dda.asgi:application --lifespan off
```
If you're using PyCharm, there's already a run configuration setup to
do each of these steps, just ensure you have the correct environment
variables updated.

# Contributing Code
We use mypy for typing, and very strictly. Run the following to run
mypy checks on your current branch:
```commandline
poetry run mypy dda/ tests/
```
This will also run in CI, preventing merge if issues are not addressed. Use
typing ignore macros sparingly.

We use ruff for formatting. Formatting is handled by precommit hooks and checked
in CI.
