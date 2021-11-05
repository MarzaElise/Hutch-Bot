from diskord.ext import commands
import diskord
from typing import *
from contextlib import suppress


class Paginator:
    def __init__(self, ctx: commands.Context, *, embeds: List[diskord.Embed]):
        self.ctx = ctx
        self.embeds = embeds
        self.bot: commands.Bot = ctx.bot
        self.index = 0
        self.current = 1
        self.timeout = 100.0
        self.compact: bool = False
        if len(self.embeds) == 2 or len(self.embeds) < 2:
            self.compact = True
        self._buttons: Dict[str, str] = {
            "⏪": "stop",
            "◀️": "plus",
            "▶️": "last",
            "⏩": "first",
            "⏹️": "minus",
        }

        if self.compact:
            keys = (
                "⏩",
                "⏪",
            )
            for key in keys:
                del self._buttons[key]

    async def send_initial_message(self):
        self.message: diskord.Message = await self.ctx.send(
            embed=self.embeds[0]
        )
        # print(self.message)
        return self.message

    async def start(self):
        await self._paginate()

    async def _paginate(self):
        """
        Start the pagination session.
        """
        message = await self.send_initial_message()
        # print(message)

        for b in self._buttons:
            await message.add_reaction(b)

        def check(
            reaction: diskord.Reaction,
            user: Union[diskord.Member, diskord.User],
        ):
            return (
                str(reaction.emoji) in self._buttons
                and user == self.ctx.author
            )

        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add", check=check, timeout=self.timeout
                )
                await self.try_delete_reaction(message, reaction)
                embed = self.get_embed(reaction)
                if not embed:
                    await message.delete()
                    break
                else:
                    await message.edit(embed=embed)

            except Exception as e:
                with suppress(diskord.Forbidden, diskord.HTTPException):
                    for b in self._buttons:
                        await message.remove_reaction(b, self.ctx.bot.user)

    def get_embed(self, reaction: diskord.Reaction):
        if str(reaction.emoji) == "⏹️":
            return None
        if str(reaction.emoji) == "▶️" and self.current != len(
            self.embeds
        ):
            self.current += 1
            return self.embeds[self.current - 1]
        if str(reaction.emoji) == "◀️" and self.current > 1:
            self.current -= 1
            return self.embeds[self.current - 1]
        if str(reaction.emoji) == "⏩":
            self.current = len(self.embeds)
            return self.embeds[self.current - 1]
        if str(reaction.emoji) == "⏪":
            self.current = 1
            return self.embeds[self.current - 1]

    async def try_delete_reaction(self, message: diskord.Message, emoji: diskord.Emoji): 
        if not message.channel.permissions_for(self.ctx.me).manage_messages:
            return False
        try:
            await message.remove_reaction(emoji, self.ctx.author)
        except Exception: # idgaf lel
            return False
