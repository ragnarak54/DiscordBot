import asyncio

from discord.ext import commands
import discord

import string

from collections import deque


class WorldTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.worlds = deque(maxlen=3)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or msg.channel.id != 789279009333575700:
            return
        try:
            # DSF bot will remove invalid world calls semi-immediately
            await asyncio.sleep(10)
            msg = await self.bot.fetch_message(msg.id)
            world = self.parse_world(msg.content)
            self.worlds.append(world)
            self.bot.loop.create_task(self.timeout_world(world))
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if reaction.message.channel.id != 789279009333575700 or reaction.emoji != '\U00002620\U0000fe0f':
            return
        try:
            self.worlds.remove(self.parse_world(reaction.message.content))
        except ValueError:
            pass

    async def timeout_world(self, world):
        await asyncio.sleep(610)
        try:
            self.worlds.remove(world)
        except ValueError:
            pass

    @staticmethod
    def parse_world(content):
        return int(content.strip(string.ascii_letters))
