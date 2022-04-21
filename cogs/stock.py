import typing

import datetime
from discord.ext import commands
from discord import app_commands
import discord

import itemlist
import merch
import output


class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='merch')
    @app_commands.guilds(discord.Object(id=439804468826210315))
    async def merch(self, interaction: discord.Interaction):
        """Displays the daily Travelling Merchant stock."""
        await interaction.response.send_message(
            embed=output.generate_merch_embed(worlds=self.bot.get_cog('WorldTracker').worlds))

    @app_commands.command(name='tomorrow')
    @app_commands.guilds(discord.Object(id=439804468826210315))
    async def tomorrow(self, interaction: discord.Interaction):
        """Displays tomorrow's stock."""
        await interaction.response.send_message(embed=output.generate_merch_embed(1))

    @app_commands.command(name='future')
    @app_commands.guilds(discord.Object(id=439804468826210315))
    async def future(self, interaction: discord.Interaction, days: app_commands.Range[int, 1, None]):
        """Displays the stock x days in the future."""
        assert days > 0, "Negative days entered"
        await interaction.response.send_message(embed=output.generate_merch_embed(days))

    @app_commands.command(name='next')
    @app_commands.guilds(discord.Object(id=439804468826210315))
    async def _next(self, interaction: discord.Interaction, item: str):
        """Finds the next time a given item will be in stock"""
        i = 1
        while i < 200:
            stock = merch.get_stock(i)
            for x in stock:
                if x.name.lower() == item.lower():
                    time = datetime.datetime.now() + datetime.timedelta(days=i)
                    await interaction.response.send_message(f'{x.name} is next in stock {i} days from now, on {time.strftime("%A, %B %d")}.')
                    return
            i += 1
        await interaction.response.send_message(f"Couldn't find {item} in the next 200 days!")

    @_next.autocomplete('item')
    async def item_autocomplete(self, interaction: discord.Interaction,
                                current: str,
                                ) -> typing.List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=item, value=item) for item in itemlist.item_list if current.lower() in item.lower()
        ]