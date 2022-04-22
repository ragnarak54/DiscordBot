import typing

from discord.ext import commands
from discord import app_commands
import discord
from fuzzywuzzy import process

import itemlist


class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_cache = {}

    @app_commands.command(name='addnotif')
    async def addnotif(self, interaction: discord.Interaction, item: str):
        """Adds an item to a user's notify list."""
        stritem = str(item).lower()
        results = get_matches(stritem, [item.lower() for item in itemlist.item_list])
        if results[0][1] != 100:
            await interaction.response.send_message(ephemeral=True,
                                                    content="Not sure what item you mean. "
                                                            "Try using the autocomplete to see valid items")
            return

        stritem = results[0][0]
        if not await self.bot.db.pref_exists(interaction.user.id, stritem):
            warning_str = ""
            if interaction.guild is None:
                warning_str = " Warning: if you leave all servers that you share with the bot, you will no longer be " \
                              "able to receive DMs and your notification list will be deleted! "
            await self.bot.db.new_pref(interaction.user, stritem)
            await interaction.response.send_message(f"Notification for {stritem} added!" + warning_str)
        else:
            await interaction.response.send_message("Already exists for this user")

    async def get_or_fetch_prefs(self, user: discord.User):
        if user.id in self.user_cache:
            return self.user_cache[user.id]
        prefs = await self.bot.db.user_prefs(user)
        self.user_cache[user.id] = prefs
        return prefs

    @addnotif.autocomplete('item')
    async def add_item_autocomplete(self, interaction: discord.Interaction,
                                current: str,
                                ) -> typing.List[app_commands.Choice[str]]:
        matching_items = [app_commands.Choice(name=item, value=item) for item in itemlist.item_list if current.lower() in item.lower()]
        return [] if len(matching_items) > 25 else matching_items

    @app_commands.command(name='removenotif')
    async def removenotif(self, interaction: discord.Interaction, item: str):
        """Removes an item from a user's notify list."""
        user_notifs = await self.get_or_fetch_prefs(interaction.user)
        if item not in user_notifs:
            await interaction.response.send_message("Not sure what item you mean. Try using the autocomplete to see valid items")
            return
        await self.bot.db.remove_pref(interaction.user.id, item)
        await interaction.response.send_message(f"Notification for {item} removed!")
        del self.user_cache[interaction.user.id]

    @removenotif.autocomplete('item')
    async def remove_item_autocomplete(self, interaction: discord.Interaction,
                                current: str,
                                ) -> typing.List[app_commands.Choice[str]]:
        item_list = await self.get_or_fetch_prefs(interaction.user)
        return [
            app_commands.Choice(name=item, value=item) for item in item_list if current.lower() in item.lower()
        ]

    @app_commands.command(name='shownotifs')
    async def shownotifs(self, interaction: discord.Interaction):
        """Shows a user's notify list"""
        data = await self.bot.db.user_prefs(interaction.user)
        if not data:
            await interaction.response.send_message("No notifications added for this user")
            return
        b = [':small_blue_diamond:' + x + '\n' for x in sorted(data)]
        user_string = f'Current notifications for {interaction.user if not interaction.guild else interaction.user.display_name}:\n'
        string = user_string + ''.join(b)
        await interaction.response.send_message(string)


def get_matches(query, choices, limit=6):
    results = process.extract(query, choices, limit=limit)
    return results
