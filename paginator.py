from discord.ext import commands, paginator as p
import discord
from typing import *
from contextlib import suppress



class Paginator:
    def __init__(self, ctx: commands.Context, *, embeds: List[discord.Embed]):
        self.ctx = ctx
        self.embeds = embeds
        self.bot: commands.Bot = ctx.bot
        self.index = 0
        self.current = 1
        self.timeout = 100.0
        self.compact: bool = False
        if len(self.embeds) == 2:
            self.compact = True
        self._buttons: Dict[str, str] = {
        "⏪": "stop",
		"◀️": "plus",
		"▶️": "last",
		"⏩": "first",
		"⏹️": "minus",
		}

        if self.compact:
            keys = ('⏩', '⏪',)
            for key in keys:
                del self._buttons[key]

    async def send_initial_message(self):
        self.message: discord.Message = await self.ctx.send(embed=self.embeds[0])
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

        def check(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
            return str(reaction.emoji) in self._buttons and user == self.ctx.author

        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for("reaction_add", check=check, timeout=self.timeout)
                if str(reaction.emoji) == "⏹️":
                    await message.delete()
                    break
                if str(reaction.emoji) == "▶️" and self.current != len(self.embeds):
                    self.current += 1
                    await message.edit(embed=self.embeds[self.current-1])
                if str(reaction.emoji) == "◀️" and self.current > 1:
                    self.current -= 1
                    await message.edit(embed=self.embeds[self.current-1])
                if str(reaction.emoji) == "⏩":
                    self.current = len(self.embeds)
                    await message.edit(embed=self.embeds[self.current-1])
                if str(reaction.emoji) == "⏪":
                    self.current = 1
                    await message.edit(embed=self.embeds[self.current-1])

            except Exception as e:
                with suppress(discord.Forbidden, discord.HTTPException):
                    for b in self._buttons:
                        await message.remove_reaction(b, self.ctx.bot.user)