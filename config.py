from typing import Any, Dict, List, Optional
import json
from pydantic import BaseSettings, BaseModel


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


class Config(BaseModel):
    BOT_TOKEN: str = None
    DEFAULT_PREFIX: str = None
    EXTENSIONS: List[str] = None
    OWNER_IDS: List[int] = None
    ME: Optional[str] = "Marcus | Bot Dev#4438"

def get_all_tokens():
    return Tokens(_env_file=".env")


def get_token(TOKEN_TYPE: str = None):
    TOKENS = get_all_tokens()
    token = TOKENS.TOKEN_2 if TOKEN_TYPE == "TOKEN_2" else TOKENS.TOKEN
    if not token:
        raise TypeError("No Token detected")
    return token

def get_config(token_type: str = "TOKEN_2"):
    with open("./assets/secrets.json", "r+") as f:
        dat = json.load(f)
    if ("BOT_TOKEN" not in dat.keys()) or (dat["BOT_TOKEN"] is None):
        dat["BOT_TOKEN"] = get_token(token_type)
    return Config(**dat)
