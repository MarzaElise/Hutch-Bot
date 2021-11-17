from tortoise import Tortoise, run_async
import models
import os


async def init():
    """
    calls Tortoise.init with our models from /models
    """
    await Tortoise.init(
        # db_url="sqlite://databases/main.sqlite",
        db_url="sqlite://:memory:",  # testing lololololololololol
        modules={"models": ["models"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas()
    await main()

async def main():
    guild = await models.GuildModel.create(id=1, name="test")
    member = await models.MemberModel.create(id=2, is_blacklisted=True, guild=guild)
    # print(await member.get_or_none(guild=guild))
    print(await (await member.get(guild=guild)).guild)
    # print(await (await guild.get(id=1)).guild)
if __name__ == '__main__':
    run_async(init())
    # run_async(main())
