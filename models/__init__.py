r"""
This folder contains all of the Tortoise ORM model classes
"""

from .guilds import GuildModel
from .members import MembeModel

from tortoise import Tortoise


async def tortoise_init():
    await Tortoise.init(
        db_url="sqlite:///databases/main.sqlite",
        modules=None,  # TODO: finish these modules shit
    )


__all__ = ("GuildModel", "MemberModel")
