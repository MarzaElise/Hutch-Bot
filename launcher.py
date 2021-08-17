import traceback
from Bot import MyBot
from BaseFile import *


def main(TOKEN: str = "TOKEN_2"):
    try:
        bot = MyBot(TOKEN)
        change_status.start(bot)
        bot.run(bot.config.BOT_TOKEN)
    except Exception as e:
        print(f"[ERROR]: \n{traceback.format_exc()}")
        return


if __name__ == "__main__":
    main("TOKEN_2")
