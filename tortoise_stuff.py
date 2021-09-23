from tortoise import Tortoise, run_async
import models
import os


async def init():
    """
    calls Tortoise.init with our models from /models
    """
    file_list = [
        f"models.{file.split('.')[0]}"  # .split('.') returns ['file', 'extension']
        for file in os.listdir("./models")
        if not file.startswith("_")
    ]
    # i will be updating that dir often so this is easy
    # if there is a better and/or easier way, plse tell me :thanks:

    await Tortoise.init(
        # db_url="sqlite://databases/main.sqlite",
        db_url="sqlite://:memory:",  # testing lololololololololol
        modules={"models": file_list},
    )
    # Generate the schema
    await Tortoise.generate_schemas()
