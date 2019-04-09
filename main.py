import asyncio
import datetime
import logging
import random
from datetime import timedelta

import config
import discord
from discord.ext import commands

import error_handler
import itemlist
import merch
import output
import userdb
from notifs import get_matches

logger = logging.getLogger('discord')
logger.setLevel(logging.CRITICAL)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''```A bot to help keep up with the Travelling Merchant's daily stock!
Made by Proclivity. If you have any questions or want the bot on your server, pm me at ragnarak54#9413.
Lets get started!\n\n'''
bot = commands.Bot(command_prefix=['?', '!'], description=description)
bot.remove_command("help")
bot.add_cog(error_handler.CommandErrorHandler(bot))
daily_messages = []


def owner_check():
    def predicate(ctx):
        return ctx.author == bot.procUser

    return commands.check(predicate)


@bot.event
async def on_ready():
    appinfo = await bot.application_info()
    bot.procUser = appinfo.owner
    output.generate_merch_image()
    output.generate_merch_image(1)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_guild_join(guild):
    if bot.procUser not in list(guild.members):
        for channel in [x for x in guild.channels if x.type == discord.ChannelType.text]:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("Please first invite my creator, ragnarak54#9413 so he can"
                                   " help set the bot up for you!")
        await guild.leave()


# background task for automatic notifications each day
async def daily_message():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.datetime.now()
        schedule_time = now.replace(hour=0, minute=1) + timedelta(days=1)
        time_left = schedule_time - now
        sleep_time = time_left.total_seconds()  # seconds from now until tomorrow at 00:01
        print(sleep_time)
        await asyncio.sleep(sleep_time)

        output.generate_merch_image()  # generate the new image for today and tomorrow
        output.generate_merch_image(1)
        items = [item.name.lower() for item in merch.get_stock()]  # get a lowercase list of today's stock
        new_stock_string = "The new stock for {0} is out!\n".format(datetime.datetime.now().strftime("%m/%d/%Y"))

        data = userdb.ah_roles(items)
        roles = set([role_tuple[0].strip() for role_tuple in data])  # get the roles for these items in AH discord

        # format the string to be sent
        tag_string = ""
        if roles != set([]):
            b = [role + '\n' for role in roles]
            tag_string = "Tags: \n" + ''.join(b)
        try:
            ah_channel = bot.get_channel(config.ah_chat_id)
            await ah_channel.send_file(file=output.today_img, content=new_stock_string + tag_string)
        except Exception as e:
            await bot.procUser.send(f"Couldn't send message to AH: {e}")

        # notify users for each item in today's stock
        for item in items:
            await auto_user_notifs(item)

        # get all the channels for daily messages, then loop through them to send messages
        # also, store them in daily_messages in case of a bad update
        daily_messages.clear()
        # TODO update DB table
        channels = [bot.get_channel(channel_tuple[0]) for channel_tuple in userdb.get_all_channels()]
        for channel in channels:
            try:
                daily_messages.append(await channel.send(file=output.today_img, content=new_stock_string))
            except discord.Forbidden:
                await bot.procUser.send(f'cant send message to {channel.name} of {channel.guild.name}')

        await asyncio.sleep(60)


@bot.command()
async def help(ctx, command=None):
    if command is None:
        commands_string = "\n?merch is the most basic command. Try it out and see what happens!" \
                          "\n\nThe bot can also notify you when certain items are in stock. Here are the useful " \
                          "commands for managing your notifications:\n" \
                          "  ?addnotif <item> : adds the item to your personal set of notifications\n" \
                          "  ?delnotif <item> : removes the item from your list\n" \
                          "  ?shownotifs : shows you what items you've added\n\n" \
                          "If you're an authorized user, you can choose to get a daily message sent to your server " \
                          "announcing when the new stock is out as soon as it's found after reset.\n" \
                          "  ?set_daily_channel <#channelname> : sets #channelname as the channel the new stock gets " \
                          "sent to.\n" \
                          "  ?daily_channel : tells you what you've currently set as your daily channel\n" \
                          "  ?toggle_daily : toggles off the daily messages. Doesn't affect any other functionality\n" \
                          "\nThanks for using my merchant bot! if you have any suggestions you can use the " \
                          "\n?suggestion <your suggestion here> \n" \
                          "and it'll send me a PM. Otherwise, feel free to contact " \
                          "me at ragnarak54#9413!```"
        await ctx.send(description + commands_string)
    else:
        if command.__doc__ is not None:
            command_string = globals()[command]
            print(str(command_string.__doc__))
            await ctx.send(str(command_string.__doc__))


@bot.command()
async def toggle_daily(ctx):
    """Toggles the daily stock message on or off for your server"""
    if userdb.is_authorized(ctx.guild, ctx.author) or ctx.author.id == config.proc:
        if userdb.remove_channel(ctx.guild):
            await ctx.send("Daily messages toggled off")
        else:
            await ctx.send(
                "Use the `?set_daily_channel` command to set which channel the daily message will be sent to")
    else:
        print(f"{ctx.author} tried to call toggle_daily!")
        await bot.procUser.send(f"{ctx.author} tried to call toggle_daily!")
        await ctx.send("You aren't authorized to do that. If there's been a mistake send me a PM!")


# PMs users who have the item preference
async def auto_user_notifs(item):
    data = userdb.users(item)
    all_users = list(bot.get_all_members())
    userlist = []
    for user_tuple in data:
        # TODO db typing
        user = discord.utils.get(all_users, id=int(user_tuple[0].strip()))
        if user is None:
            print(f"{user_tuple[0]} wasn't found! pref for {item} removed")
            userdb.remove_pref(user_tuple[0].strip(), item)
        else:
            userlist.append(user)
    print("users for {0}: ".format(item))
    for user in userlist:
        try:
            if item == "uncharted island map":
                await bot.send_file(user, output.today_img, content="the new stock is out!")
            else:
                await bot.send_message(user, "{0} is in stock!".format(item))
            print(user)
        except discord.InvalidArgument:
            print("left their server!")
        except AttributeError:
            print("left their server!")
        except discord.Forbidden:
            print(f"forbidden: cannot send message to {user}")


@bot.command(name='ah_merch')
async def ah_test(ctx):
    """Tags the relevant roles in AH discord for the daily stock"""
    if ctx.author.top_role >= discord.utils.get(ctx.guild.roles, id=config.ah_mod_role) \
            or ctx.author.id == config.proc:
        items = [item.name for item in merch.get_stock()]
        data = userdb.ah_roles(items)
        roles = [role_tuple[0].strip() for role_tuple in data]
        b = [role + '\n' for role in roles]
        tag_string = "Tags: " + ''.join(b)
        await ctx.send(discord.Object(id=config.ah_chat_id), tag_string)


@bot.command()
async def user_notifs(ctx, *, item):
    """Notifies users who have the input preference"""
    if ctx.author.id == config.proc or userdb.is_authorized(ctx.guild, ctx.author):
        data = userdb.users(item)
        users = [user_tuple[0].strip() for user_tuple in data]
        for user in users:
            print(user)
            # TODO: update DB table
            member = bot.get_guild(userdb.user_server(user)).get_member(user_id=user)
            await member.send(f"{item} is in stock!")
            print(user)
    else:
        print(f"{ctx.author} tried to call user_notifs!")
        await bot.procUser.send(f"{ctx.author} tried to call user_notifs!")
        await ctx.send("This command isn't for you!")


@bot.command()
async def force_notifs(ctx):
    """Notifies users for today's stock"""
    if ctx.author == bot.procUser:
        items = [item.name.lower() for item in merch.get_stock()]
        for item in items:
            await auto_user_notifs(item)
    else:
        await bot.procUser.send(f"{ctx.author} tried to call notif_test!")
        await ctx.send("This command isn't for you!")


@bot.command(name='merch', aliases=['merchant', 'shop', 'stock'])
async def merchant(ctx):
    """Displays the daily Traveling merchant stock."""
    now = datetime.datetime.now()
    member = ctx.author
    channel = ctx.channel
    guild = ctx.guild
    print(f'called at {now.strftime("%H:%M")} by {member} in {channel} of {guild}')
    date_message = f'The stock for {now.strftime("%m/%d/%Y")}:'
    await ctx.send(file=output.today_img, content=date_message)
    if not userdb.user_exists(ctx.author.id):
        print(f"user {ctx.author} doesn't have any preferences")
        chance = random.random()
        if chance < 0.1:
            await ctx.send("Don't forget to try out the ?addnotif <item> function so you don't "
                           "have to check the stock every day!")


@bot.command(aliases=['tmrw', 'tommorow'])
async def tomorrow(ctx):
    tmrw = datetime.datetime.now() + datetime.timedelta(days=1)
    date_message = "The stock for tomorrow, " + tmrw.strftime("%m/%d/%Y") + ":"
    await ctx.send(output.tomorrow_img, content=date_message)


@bot.command()
async def future(ctx, days: int):
    assert days > 0, "Negative days entered"
    day = datetime.datetime.now() + datetime.timedelta(days=days)
    date_message = "The stock for " + day.strftime("%m/%d/%Y") + ":"
    if days == 1:
        await ctx.send(output.tomorrow_img, content=date_message)
        return
    output.generate_merch_image(days)
    await ctx.send(output.custom_img, content=date_message)


@bot.command(name="next")
async def _next(ctx, *, item):
    await ctx.trigger_typing()
    stritem = str(item).lower()
    lst = [item.lower() for item in itemlist.item_list]
    results = get_matches(stritem, lst)
    if stritem not in lst:
        if results[0][1] - results[1][1] < 20:
            if results[1][1] > 80:
                suggestions = [x[0] for x in results if x[1] > 80]
                b = [':small_blue_diamond:' + x + '\n' for x in suggestions]
                await ctx.send("Make sure you're spelling your item correctly! Maybe you meant to type one of these:\n"
                               + "".join(b))
                return
        if results[0][1] < 75:
            await ctx.send("Make sure you're spelling your item correctly!\nCheck your PMs for a list of correct "
                           "spellings, or refer to the wikia page.")
            b = sorted([item + '\n' for item in itemlist.item_list])
            itemstrv2 = ''.join(b)
            await ctx.author.send('Possible items:\n' + itemstrv2)
            return
    stritem = results[0][0]
    i = 1
    while i < 200:
        stock = merch.get_stock(i)
        for x in stock:
            if x.name.lower() == stritem:
                time = datetime.datetime.now() + datetime.timedelta(days=i)
                await ctx.send(f'{x.name} is next in stock {i} days from now, on {time.strftime("%A, %B %d")}.')
                return
        i += 1
    await ctx.send(f"Couldn't find {stritem} in the next 200 days!")


@bot.command()
async def update(ctx):
    if ctx.author == bot.procUser or userdb.is_authorized(ctx.guild, ctx.author):
        output.generate_merch_image()
        output.generate_merch_image(1)
        await ctx.send(file=output.today_img, content="Stock updated. If this stock is still "
                                                      "incorrect, send my owner @ragnarak54"
                                                      "#9413 a message.")
    else:
        print(f"{ctx.author} tried to call update!")
        await bot.procUser.send(f"{ctx.author} tried to call update!")
        await ctx.send("You aren't authorized to do that. If there's been a mistake send me a PM!")


@bot.command(aliases=["fix_daily_messages"])
async def fix_daily_message(ctx, delete=None):
    if ctx.author == bot.procUser or userdb.is_authorized(ctx.guild, ctx.author):
        output.generate_merch_image()
        new_stock_string = f'The new stock for {datetime.datetime.now().strftime("%m/%d/%Y")} is out!\n'
        channels = [bot.get_channel(int(channel_tuple[0].strip())) for channel_tuple in userdb.get_all_channels()]
        if delete == "delete" and daily_messages is not None:
            for message in daily_messages:
                await message.delete()
        for channel in channels:
            await channel.send(output.today_img, content=new_stock_string)
        items = [item.name.lower() for item in merch.get_stock()]  # get a lowercase list of today's stock
        data = userdb.ah_roles(items)
        roles = set([role_tuple[0].strip() for role_tuple in data])  # get the roles for these items in AH discord
        # format the string to be sent
        tag_string = ""
        if roles != set([]):
            b = [role + '\n' for role in roles]
            tag_string = "Tags: \n" + ''.join(b)
        ah_channel = bot.get_channel(config.ah_chat_id)
        await ah_channel.send(output.today_img, content=new_stock_string + tag_string)

    else:
        print(f"{ctx.author} tried to call fix daily messages!")
        await bot.procUser.send(f"{ctx.author} tried to call fix daily messages!")
        await ctx.send("You aren't authorized to do that. If there's been a mistake send me a PM!")


@bot.command()
@owner_check()
async def restart_background(ctx):
    bot.daily_background.cancel()
    try:
        await bot.daily_background
    except asyncio.CancelledError:
        await bot.procUser.send("successfully canceled previous task before restarting")
    else:
        await bot.procUser.send("No background tasks to cancel")
    bot.daily_background = bot.loop.create_task(daily_message())
    await bot.procUser.send("Task restarted")


@bot.command()
@owner_check()
async def message_channels(ctx, *, string):
    channels = [bot.get_channel(int(channel_tuple[0].strip())) for channel_tuple in userdb.get_all_channels()]
    mass_messages = []
    embed = discord.Embed()
    embed.description = string
    embed.colour = discord.Colour.dark_blue()
    for channel in channels:
        try:
            mass_messages.append(await channel.send(embed=embed))
        except discord.Forbidden:
            print(f"cant send message to channel {channel}!")
            pass


@bot.command()
@owner_check()
async def message_users(ctx, *, string):
    all_ids = [user_tuple[0] for user_tuple in userdb.get_all_users()]
    all_users = []
    members = list(bot.get_all_members())
    for id_ in all_ids:
        user = discord.utils.get(members, id=id_)
        if user is not None:
            all_users.append(user)
    for user in all_users:
        try:
            await user.send(string)
        except discord.Forbidden:
            print(f"cant send message to {user}")


@bot.command()
async def users(ctx, *, item):
    if ctx.author.id == config.proc:
        userlist = [user_tuple[0].strip() for user_tuple in userdb.users(item)]
        await ctx.send(userlist)


@bot.command()
async def authorize(ctx, user: discord.Member):
    if ctx.author == bot.procUser or userdb.is_authorized(ctx.guild, ctx.author):
        userdb.authorize_user(ctx.message.server, user)
        await ctx.send(f"{user} authorized")
        print(f"{user} authorized")
    else:
        print(f"{ctx.author} tried to call authorize!")
        await bot.procUser.send(f"{ctx.author} tried to call authorize!")
        await ctx.send("You aren't authorized to do that. If there's been a mistake send me a PM!")


@bot.command()
async def unauthorize(ctx, user: discord.Member):
    if ctx.author == bot.procUser:
        if userdb.is_authorized(ctx.guild, user):
            userdb.unauthorize_user(ctx.guild, user)
            await ctx.send(f"{user} unauthorized.")
        else:
            await ctx.send("{user} isn't authorized")
    else:
        print(f"{ctx.author} tried to call unauthorize!")
        await bot.procUser.send(f"{ctx.author} tried to call unauthorize!")
        await ctx.author("You aren't authorized to do that. If there's been a mistake send me a PM!")


@bot.command()
async def set_daily_channel(ctx, new_channel: discord.TextChannel):
    """A command for authorized users to set or update the channel that receives the daily stock message"""
    if userdb.is_authorized(ctx.guild, ctx.author) or ctx.author.id == config.proc:
        new = userdb.update_channel(ctx.guild, new_channel.id)
        if new:
            await ctx.send("Channel set")
        else:
            await ctx.send("Channel settings updated")
    else:
        print(f"{ctx.author} tried to call set daily channel!")
        await bot.procUser.send(f"{ctx.author} tried to call set daily channel!")
        await ctx.send("You aren't authorized to do that. If there's been a mistake send me a PM!")


@bot.command(aliases=['channel', 'current_channel'])
async def daily_channel(ctx):
    if userdb.is_authorized(ctx.guild, ctx.author) or ctx.author == bot.procUser:
        channel = userdb.get_current_channel(ctx.guild)
        if channel is not None:
            await ctx.send(f"Currently set to <#{(channel[0])[0].strip()}>.\nUse the `?set_daily_channel` command to "
                           f"change this.")
        else:
            await ctx.send("No channel currently set. Use the `?set_daily_channel` command to change this.")


@bot.command()
async def suggestion(ctx, *, string):
    """Sends a message to me with your suggestion!"""
    await bot.procUser.send(f"{ctx.author} says: {string}")
    await ctx.send("Thanks for the suggestion!")


@bot.command(name='3amerch', category='memes')
async def third_age_merch(ctx):
    """:("""
    if ctx.author == bot.procUser:
        await ctx.send("-500m")
    else:
        await ctx.send("!kms")


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""

    for choice in choices:
        if "proc" in choice:
            await ctx.send(choice)
            return
        if "nex" in choice:
            await ctx.send(choice)
            return
        if "kk" in choices:
            await ctx.send(choice)
            return
    await ctx.send(random.choice(choices))


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined in {member.joined_at}')


@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not cool')


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')


@cool.command(name='proc')
async def _proc(ctx):
    """Is proc cool?"""
    await ctx.send('Yes, proc is cool.')


bot.daily_background = bot.loop.create_task(daily_message())
bot.run(config.token)
