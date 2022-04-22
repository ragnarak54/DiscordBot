import discord
from discord.ext import commands


class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            await self.bot.db.log_command(interaction.command.name, interaction.guild.id, interaction.user.id, "slash")

    @commands.Cog.listener()
    async def on_command(self, ctx: discord.ext.commands.Context):
        await self.bot.db.log_command(ctx.command.name, ctx.guild.id, ctx.author.id, "message")
