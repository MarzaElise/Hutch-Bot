from pydantic import BaseSettings
from typing import Dict, Any


class Passwords(BaseSettings):
    REDDIT_PASS: str
    REDDIT_CLIENT_ID: str
    REDDIT_CLIENT_SECRET: str  # reddit pass, client is and client secret for asyncpraw :lol:
    PGAMER_X_API_KEY: str  # pgamerX API key for the AI chat


def get_passwords():
    settings = Passwords(_env_file="passwords.env")
    return settings


class Tokens(BaseSettings):
    TOKEN: str  # main bot token
    TOKEN_2: str  # development bot token
    # ME: str # sussy baka
