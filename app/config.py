import os


DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

ASYNC_DB_DRIVER = "postgresql+asyncpg"
SYNC_DB_DRIVER = "postgresql+asyncpg"

base_url = f"{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SYNC_DB_URL = f"{SYNC_DB_DRIVER}://{base_url}"
ASYNC_DB_URL = f"{ASYNC_DB_DRIVER}://{base_url}"
