from tortoise import Tortoise


async def tortoise_init():
    await Tortoise.init(
        db_url="sqlite:///databases/main.sqlite",
        modules=None,  # TODO: finish these modules shit
    )
