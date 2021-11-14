import traceback

from BaseFile import *
from Bot import MyBot


def main(TOKEN: str = "TOKEN"):
    bot = MyBot(TOKEN)
    change_status.start(bot)
    if TOKEN == "TOKEN_2":
        bot.command_prefix = ">"
        print("[INFO]: Running Test bot with > prefix")
    try:
        bot.run(bot.config.BOT_TOKEN)
    except Exception as e:
        print(f"[ERROR]: {e.__class__.__name__} \n{traceback.format_exc()}")
        return


if __name__ == "__main__":
    main("TOKEN_2")
    # main()
