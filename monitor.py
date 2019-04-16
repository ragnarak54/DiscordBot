import discord
from discord.ext import commands
import userdb


class Monitor(commands.Cog):

    def __init__(self, bot, server):
        self.bot = bot
        self.server = server
        mapped_channels = [x[0] for x in userdb.get_id_table()]
        channels = [int(channel_tuple[0]) for channel_tuple in userdb.get_all_channels()]
        for channel in channels:
            if channel not in mapped_channels:
                self.bot.loop.create_task(self.create_channel(ctx=self.bot.get_channel(channel)))
        table = userdb.get_id_table()
        self.id_table = {}
        for mapping in table:
            print(f'mapping {mapping[0]} to {mapping[1]}')
            self.id_table[mapping[0]] = mapping[1]

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        print(ctx.guild.channels)
        if ctx.command.name == "set_daily_channel":

            server = self.server
            channels = [x.name for x in server.channels]
            if f'{ctx.guild.name}-{ctx.args[1]}' not in channels:
                await self.create_channel(new=True, ctx=ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot and message.author != self.bot.user:
            return
        if message.channel.id in self.id_table:
            try:
                channel = self.bot.get_channel(self.id_table[message.channel.id])
                if message.author == self.bot.user:
                    await channel.send("I replied!")
                elif message.content == '':
                    await channel.send(f'{message.author.nick}: non-text message')
                else:
                    await channel.send(f'{message.author.nick}: {message.content}')
            except Exception as e:
                await self.bot.get_channel(self.id_table[message.channel.id]).send(f"Couldn't send a message: {e}")

    async def create_channel(self, new=False, ctx=None, ):
        if new:
            channel = await self.server.create_text_channel(f'{ctx.guild.name}-{ctx.args[1].name}',
                                                            category=self.bot.get_channel(566048042323804161))
            userdb.insert_new_mapping(ctx.args[1].id, ctx.args[1].name, channel.id)
        else:
            channel = await self.server.create_text_channel(f'{ctx.guild.name}-{ctx.name}',
                                                            category=self.bot.get_channel(566048042323804161))
            userdb.insert_new_mapping(ctx.id, ctx.name, channel.id)
