import typing

from discord.ext import commands
from discord import app_commands
import discord
from fuzzywuzzy import process

import itemlist
import userdb


class NotificationsLegacy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['newnotif'])
    async def addnotif(self, ctx, *, item):
        """Adds an item to a user's notify list."""
        stritem = str(item).lower()
        lst = [item.lower() for item in itemlist.item_list]
        results = get_matches(stritem, lst)
        if ctx.guild is None:
            if discord.utils.get(self.bot.get_all_members(), id=ctx.message.author.id) is None:
                await ctx.send("Bots aren't allowed to send DMs to users who aren't in a shared server with the bot. "
                               "Try adding a notification in a server instead of DM.\n"
                               "If you want the bot added to a server you're in, send me a message @ragnarak54#9413.")

        if stritem not in lst:
            if results[0][1] - results[1][1] < 20:
                if results[1][1] > 80:
                    suggestions = [x[0] for x in results if x[1] > 80]
                    b = [':small_blue_diamond:' + x + '\n' for x in suggestions]
                    await ctx.message.add_reaction('\U0000274c')
                    await ctx.send(
                        "Make sure you're spelling your item correctly! Maybe you meant to type one of these:\n"
                        + "".join(b))
                    return

            if results[0][1] < 75:
                await ctx.message.add_reaction('\U0000274c')
                await ctx.send("Make sure you're spelling your item correctly!\nCheck your PMs for a list of correct "
                               "spellings, or refer to the wikia page.")
                b = sorted([item + '\n' for item in itemlist.item_list])
                itemstrv2 = ''.join(b)
                await ctx.author.send(f'Possible items:\n{itemstrv2}')
                return

        stritem = results[0][0]
        if not await self.bot.db.pref_exists(ctx.author.id, stritem):
            warning_str = ""
            if ctx.guild is None:
                warning_str = " Warning: if you leave all servers that you share with the bot, you will no longer be " \
                              "able to receive DMs and your notification list will be deleted! "
            await self.bot.db.new_pref(ctx.author, stritem)
            await ctx.send(f"Notification for {stritem} added!" + warning_str)
            await ctx.message.add_reaction('\U00002705')
            print(f"{ctx.author} added notification for {item} in {ctx.guild}")
        else:
            await ctx.message.add_reaction('\U0000274c')
            await ctx.send("Already exists for this user")

    @commands.command(aliases=['delnotif', 'remnotif', 'deletenotif'])
    async def removenotif(self, ctx, *, item):
        """Removes an item from a user's notify list."""
        stritem = str(item).lower()
        notifs = await self.bot.db.user_prefs(ctx.author)
        results = get_matches(stritem, notifs)
        if stritem not in notifs:
            if results[0][1] > 75:
                stritem = results[0][0]
            elif len(notifs) > 1 and results[0][1] - results[1][1] < 20:
                if results[1][1] > 80:
                    suggestions = [x[0] for x in results if x[1] > 80]
                    b = [':small_blue_diamond:' + x + '\n' for x in suggestions]
                    await ctx.send("You don't have that preference. Maybe you meant:\n" + "".join(b))
                    return

        if await self.bot.db.pref_exists(ctx.author.id, stritem):
            await self.bot.db.remove_pref(ctx.author.id, stritem)
            await ctx.message.add_reaction('\U00002705')
            await ctx.send(f"Notification for {stritem} removed!")
        else:
            await ctx.message.add_reaction('\U0000274c')
            await ctx.send("You don't have that preference")

    @commands.command()
    async def adnotif(self, ctx, *, item):
        if ctx.author == self.bot.procUser or await self.bot.db.is_authorized(ctx.author):
            stritem = str(item)
            if not await self.bot.db.pref_exists(ctx.author.id, stritem):
                await self.bot.db.new_pref(ctx.author, stritem)
                await ctx.send(f"Notification for {stritem} added!")
            else:
                await ctx.send("Already exists for this user")

    @commands.command(aliases=['notifs', 'mynotifs'])
    async def shownotifs(self, ctx):
        """Shows a user's notify list"""
        data = await self.bot.db.user_prefs(ctx.author)
        if not data:
            await ctx.send("No notifications added for this user")
            return
        b = [':small_blue_diamond:' + x + '\n' for x in sorted(data)]
        user_string = f'Current notifications for {ctx.author if not ctx.guild else ctx.author.display_name}:\n'
        string = user_string + ''.join(b)
        await ctx.send(string)


def get_matches(query, choices, limit=6):
    results = process.extract(query, choices, limit=limit)
    return results
