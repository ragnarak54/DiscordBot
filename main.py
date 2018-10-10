import discord
from discord.ext import commands
import output
from datetime import timedelta
import datetime
import logging
import config
import userdb
import asyncio
import request
import itemlist
import random
import merch
from fuzzywuzzy import process
import error_handler


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
        return ctx.message.author == bot.procUser
    return commands.check(predicate)


@bot.event
async def on_ready():
    appinfo = await bot.application_info()
    bot.procUser = appinfo.owner
    output.generate_merch_image()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# background task for automatic notifications each day
async def daily_message():
    await bot.wait_until_ready()
    while not bot.is_closed:
        now = datetime.datetime.now()
        schedule_time = now.replace(hour=0, minute=2) + timedelta(days=1)
        time_left = schedule_time - now
        sleep_time = time_left.total_seconds()  # seconds from now until tomorrow at 00:02
        print(sleep_time)
        await asyncio.sleep(sleep_time)

        now2 = datetime.datetime.today()
        # Check the wiki's date to see if it's current. If not, try again in 60 seconds
        while not now2.day == int(request.parse_stock_date()):
            print(now2.day)
            print(request.parse_stock_date())
            await asyncio.sleep(60)

        output.generate_merch_image()  # generate the new image
        items = [item.name.lower() for item in request.parse_merch_items()]  # get a lowercase list of today's stock
        new_stock_string = "The new stock for {0} is out!\n".format(datetime.datetime.now().strftime("%m/%d/%Y"))

        data = userdb.ah_roles(items)
        roles = set([role_tuple[0].strip() for role_tuple in data])  # get the roles for these items in AH discord

        # format the string to be sent
        tag_string = ""
        if roles != set([]):
            b = [role + '\n' for role in roles]
            tag_string = "Tags: \n" + ''.join(b)
        ah_channel = bot.get_channel(config.ah_chat_id)
        await bot.send_file(ah_channel, output.output_img, content=new_stock_string + tag_string)

        # notify users for each item in today's stock
        for item in items:
            await auto_user_notifs(item)

        # get all the channels for daily messages, then loop through them to send messages
        # also, store them in daily_messages in case of a bad wiki update
        daily_messages.clear()
        channels = [bot.get_channel(channel_tuple[0].strip()) for channel_tuple in userdb.get_all_channels()]
        for channel in channels:
            try:
                daily_messages.append(await bot.send_file(channel, output.output_img, content=new_stock_string))
            except discord.Forbidden:
                pass

        await asyncio.sleep(60)

@bot.event
async def on_at(message):
    await bot.process_commands(message)

@bot.command()
async def help(command=None):
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
        await bot.say(description + commands_string)
    else:
        if command.__doc__ is not None:
            command_string = globals()[command]
            print(str(command_string.__doc__))
            await bot.say(str(command_string.__doc__))


@bot.command(pass_context=True)
async def toggle_daily(ctx):
    """Toggles the daily stock message on or off for your server"""
    if userdb.is_authorized(ctx.message.server, ctx.message.author) or ctx.message.author.id == config.proc:
        if userdb.remove_channel(ctx.message.server):
            await bot.say("Daily messages toggled off")
        else:
            await bot.say("Use the `?set_daily_channel` command to set which channel the daily message will be sent to")
    else:
        print("{0} tried to call toggle_daily!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call toggle_daily!".format(ctx.message.author))
        await bot.say("You aren't authorized to do that. If there's been a mistake send me a PM!")

# PMs users who have the item preference
async def auto_user_notifs(item):
    data = userdb.users(item)
    all_users = list(bot.get_all_members())
    userlist = []
    for user_tuple in data:
        user = discord.utils.get(all_users, id=user_tuple[0].strip())
        if user is None:
            print("{0} wasn't found! pref for {1} removed".format(user_tuple[0], item))
            userdb.remove_pref(user_tuple[0].strip(), item)
        else:
            userlist.append(user)
    print("users for {0}: ".format(item))
    for user in userlist:
        try:
            if item == "uncharted island map":
                await bot.send_file(user, output.output_img, content="the new stock is out!")
            else:
                await bot.send_message(user, "{0} is in stock!".format(item))
            print(user)
        except discord.InvalidArgument:
            print("left their server!")
        except AttributeError:
            print("left their server!")
        except discord.Forbidden:
            print("forbidden: cannot send message to {0}".format(user))


@bot.command(pass_context=True, name='ah_merch')
async def ah_test(ctx):
    """Tags the relevant roles in AH discord for the daily stock"""
    if ctx.message.author.top_role >= discord.utils.get(ctx.message.server.roles, id=config.ah_mod_role) \
            or ctx.message.author.id == config.proc:
        items = [item.name for item in request.parse_merch_items()]
        data = userdb.ah_roles(items)
        roles = [role_tuple[0].strip() for role_tuple in data]
        b = [role + '\n' for role in roles]
        tag_string = "Tags: " + ''.join(b)
        await bot.send_message(discord.Object(id=config.ah_chat_id), tag_string)
    else:
        return

@bot.command(pass_context=True)
async def user_notifs(ctx, *, item):
    """Notifies users who have the input preference"""
    if ctx.message.author.id == config.proc or userdb.is_authorized(ctx.message.server, ctx.message.author):
        data = userdb.users(item)
        users = [user_tuple[0].strip() for user_tuple in data]
        for user in users:
            print(user)
            member = bot.get_server(userdb.user_server(user)).get_member(user_id=user)
            await bot.send_message(member, "{0} is in stock!".format(item))
            print(user)
    else:
        print("{0} tried to call user_notifs!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call user_notifs!".format(ctx.message.author))
        await bot.say("This command isn't for you!")

@bot.command(pass_context=True)
async def force_notifs(ctx):
    """Notifies users for today's stock"""
    if ctx.message.author.id == config.proc:
        items = [item.name.lower() for item in request.parse_merch_items()]
        for item in items:
            await auto_user_notifs(item)
    else:
        print("{0} tried to call notif_test!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call notif_test!".format(ctx.message.author))
        await bot.say("This command isn't for you!")

@bot.command(pass_context=True, name='merch', aliases=['merchant', 'shop', 'stock'])
async def merchant(ctx):
    """Displays the daily Traveling merchant stock."""
    now2 = datetime.datetime.today()
    if now2.day == int(request.parse_stock_date()):
        now = datetime.datetime.now()
        member = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server
        logger.info("called at " + now.strftime("%H:%M") + ' by {0} in {1} of {2}'.format(member, channel, server))
        print("called at " + now.strftime("%H:%M") + ' by {0} in {1} of {2}'.format(member, channel, server))
        date_message = "The stock for " + now.strftime("%m/%d/%Y") + ":"
        await bot.send_file(ctx.message.channel, output.output_img, content=date_message)
        if not userdb.user_exists(ctx.message.author.id):
            print("user {0} doesn't have any preferences".format(ctx.message.author))
            chance = random.random()
            if chance < 0.1:
                await bot.say("Don't forget to try out the ?addnotif <item> function so you don't "
                              "have to check the stock every day!")
    else:
        await bot.say("The new stock isn't out yet!")

@bot.command(pass_context=True)
async def update(ctx):
    if ctx.message.author == bot.procUser or userdb.is_authorized(ctx.message.server, ctx.message.author):
        output.generate_merch_image()
        await bot.send_file(ctx.message.channel, output.output_img, content="Stock updated. If this stock is still "
                                                                            "incorrect, verify that "
                                                                            "the wiki has the correct stock, then try "
                                                                            "again.")
    else:
        print("{0} tried to call update!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call update!".format(ctx.message.author))
        await bot.say("You aren't authorized to do that. If there's been a mistake send me a PM!")

@bot.command(pass_context=True, aliases=["fix_daily_messages"])
async def fix_daily_message(ctx):
    if ctx.message.author == bot.procUser or userdb.is_authorized(ctx.message.server, ctx.message.author):
        output.generate_merch_image()
        new_stock_string = "The new stock for {0} is out!\n".format(datetime.datetime.now().strftime("%m/%d/%Y"))
        channels = [bot.get_channel(channel_tuple[0].strip()) for channel_tuple in userdb.get_all_channels()]
        if daily_messages is not None:
            for message in daily_messages:
                await bot.delete_message(message)
        for channel in channels:
            await bot.send_file(channel, output.output_img, content=new_stock_string)
        items = [item.name.lower() for item in request.parse_merch_items()]  # get a lowercase list of today's stock
        data = userdb.ah_roles(items)
        roles = set([role_tuple[0].strip() for role_tuple in data])  # get the roles for these items in AH discord
        # format the string to be sent
        tag_string = ""
        if roles != set([]):
            b = [role + '\n' for role in roles]
            tag_string = "Tags: \n" + ''.join(b)
        ah_channel = bot.get_channel(config.ah_chat_id)
        await bot.send_file(ah_channel, output.output_img, content=new_stock_string + tag_string)
    else:
        print("{0} tried to call fix daily messages!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call fix daily messages!".format(ctx.message.author))
        await bot.say("You aren't authorized to do that. If there's been a mistake send me a PM!")

@bot.command(pass_context=True)
async def restart_background(ctx):
    if ctx.message.author == bot.procUser or userdb.is_authorized(ctx.message.server, ctx.message.author):
        await daily_message().close()
        bot.loop.create_task(daily_message())


@bot.command()
@owner_check()
async def message_channels(*, string):
    channels = [bot.get_channel(channel_tuple[0].strip()) for channel_tuple in userdb.get_all_channels()]
    mass_messages = []
    embed = discord.Embed()
    embed.description = string
    embed.colour = discord.Colour.dark_blue()
    for channel in channels:
        try:
            mass_messages.append(await bot.send_message(channel, embed=embed))
        except discord.Forbidden:
            print("cant send message to channel {0}!".format(channel))
            pass


@bot.command()
@owner_check()
async def message_users(*, string):
    all_ids = [user_tuple[0] for user_tuple in userdb.get_all_users()]
    all_users = []
    members = list(bot.get_all_members())
    for id_ in all_ids:
        user = discord.utils.get(members, id=id_)
        if user is not None:
            all_users.append(user)
    for user in all_users:
        try:
            await bot.send_message(user, string)
        except discord.Forbidden:
            print("cant send message to {0}".format(user))


@bot.command(pass_context=True, aliases=['newnotif'])
async def addnotif(ctx, *, item):
    """Adds an item to a user's notify list."""
    stritem = str(item).lower()
    lst = [item.lower() for item in itemlist.item_list]
    results = get_matches(stritem, lst)
    if ctx.message.server is None:
        if discord.utils.get(bot.get_all_members(), id=ctx.message.author.id) is None:
            await bot.say("Bots aren't allowed to send DMs to users who aren't in a shared server with the bot. "
                          "Try adding a notification in a server instead of DM.\n"
                          "If you want the bot added to a server you're in, send me a message @ragnarak54#9413.")
    if stritem not in lst:
        if results[0][1] - results[1][1] < 20:
            if results[1][1] > 80:
                suggestions = [x[0] for x in results if x[1] > 80]
                b = [':small_blue_diamond:' + x + '\n' for x in suggestions]
                await bot.say("Make sure you're spelling your item correctly! Maybe you meant to type one of these:\n"
                              + "".join(b))
                return
        if results[0][1] < 75:
            await bot.say("Make sure you're spelling your item correctly!\nCheck your PMs for a list of correct "
                          "spellings, or refer to the wikia page.")
            b = sorted([item + '\n' for item in itemlist.item_list])
            itemstrv2 = ''.join(b)
            await bot.send_message(ctx.message.author, 'Possible items:\n'+itemstrv2)
            return
    stritem = results[0][0]
    if not userdb.pref_exists(ctx.message.author.id, stritem):
        if ctx.message.server is None:
            await bot.say("Warning: if you leave all servers that you share with the bot, you will no longer be able"
                          " to receive DMs and your notification list will be deleted!")
            userdb.new_pref(ctx.message.author.id, ctx.message.author, stritem, "direct message")
        else:
            userdb.new_pref(ctx.message.author.id, ctx.message.author, stritem, ctx.message.server.id)
        await bot.say("Notification for {0} added!".format(stritem))
        print("{0} added notification for {1} in {2}".format(ctx.message.author, item, ctx.message.server))
    else:
        await bot.say("Already exists for this user")

@bot.command(pass_context=True)
async def adnotif(ctx, *, item):
    if userdb.is_authorized(ctx.message.server, ctx.message.author) or ctx.message.author == bot.procUser:
        stritem = str(item)
        if not userdb.pref_exists(ctx.message.author.id, stritem):
            if ctx.message.server is None:
                userdb.new_pref(ctx.message.author.id, ctx.message.author, stritem, "direct message")
            else:
                userdb.new_pref(ctx.message.author.id, ctx.message.author, stritem, ctx.message.server.id)
            await bot.say("Notification for {0} added!".format(stritem))
        else:
            await bot.say("Already exists for this user")


def get_matches(query, choices, limit=6):
    results = process.extract(query, choices, limit=limit)
    return results

@bot.command(pass_context=True, aliases=['delnotif', 'remnotif', 'deletenotif'])
async def removenotif(ctx, *, item):
    """Removes an item from a user's notify list."""
    stritem = str(item).lower()
    data = userdb.user_prefs(ctx.message.author.id)
    notifs = [data_tuple[0].strip() for data_tuple in data]
    results = get_matches(stritem, notifs)
    if stritem not in notifs:
        if results[0][1] - results[1][1] < 20:
            if results[1][1] > 80:
                suggestions = [x[0] for x in results if x[1] > 80]
                b = [':small_blue_diamond:' + x + '\n' for x in suggestions]
                await bot.say("You don't have that preference. Maybe you meant:\n" + "".join(b))
                return
    if results[0][1] > 75:
        stritem = results[0][0]
    if userdb.pref_exists(ctx.message.author.id, stritem):
        userdb.remove_pref(ctx.message.author.id, stritem)
        await bot.say("Notification for {0} removed!".format(stritem))
    else:
        await bot.say("user does not have this preference")

@bot.command(pass_context=True, aliases=['notifs', 'mynotifs'])
async def shownotifs(ctx):
    """Shows a user's notify list"""
    data = userdb.user_prefs(ctx.message.author.id)
    if not data:
        await bot.say("No notifications added for this user")
        return
    notifs = sorted([data_tuple[0].strip() for data_tuple in data])
    b = [':small_blue_diamond:' + x + '\n' for x in notifs]
    # check if called in a direct message with the bot
    if not ctx.message.server or not ctx.message.author.nick:
        user_string = 'Current notifications for {0}:\n'.format(ctx.message.author)
    else:
        user_string = 'Current notifications for {0}:\n'.format(ctx.message.author.nick)
    string = user_string + ''.join(b)
    await bot.say(string)

@bot.command(pass_context=True)
async def users(ctx, *, item):
    if ctx.message.author.id == config.proc:
        userlist = [user_tuple[0].strip() for user_tuple in userdb.users(item)]
        await bot.say(userlist)

@bot.command(pass_context=True)
async def authorize(ctx, user: discord.Member):
    if ctx.message.author.id == config.proc or userdb.is_authorized(ctx.message.server, ctx.message.author):
        userdb.authorize_user(ctx.message.server, user)
        await bot.say("{0} authorized".format(user))
        print("{0} authorized".format(user))
    else:
        print("{0} tried to call authorize!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call authorize!".format(ctx.message.author))
        await bot.say("You aren't authorized to do that. If there's been a mistake send me a PM!")

@bot.command(pass_context=True)
async def unauthorize(ctx, user: discord.Member):
    if ctx.message.author == bot.procUser:
        if userdb.is_authorized(ctx.message.server, user):
            userdb.unauthorize_user(ctx.message.server, user)
            await bot.say("{0} unauthorized.".format(user))
        else:
            await bot.say("{0} isn't authorized".format(user))
    else:
        print("{0} tried to call unauthorize!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call unauthorize!".format(ctx.message.author))
        await bot.say("You aren't authorized to do that. If there's been a mistake send me a PM!")


@bot.command(pass_context=True)
async def set_daily_channel(ctx, new_channel: discord.Channel):
    """A command for authorized users to set or update the channel that receives the daily stock message"""
    if userdb.is_authorized(ctx.message.server, ctx.message.author) or ctx.message.author.id == config.proc:
        new = userdb.update_channel(ctx.message.server, new_channel.id)
        if new:
            await bot.say("Channel set")
        else:
            await bot.say("Channel settings updated")
    else:
        print("{0} tried to call set daily channel!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call set daily channel!".format(ctx.message.author))
        await bot.say("You aren't authorized to do that. If there's been a mistake send me a PM!")

@bot.command(pass_context=True, aliases=['channel', 'current_channel'])
async def daily_channel(ctx):
    if userdb.is_authorized(ctx.message.server, ctx.message.author) or ctx.message.author.id == config.proc:
        channel = userdb.get_current_channel(ctx.message.server)
        if channel is not None:
            await bot.say("Currently set to <#" + str((channel[0])[0].strip()) + ">.\nUse the `?set_daily_channel` command to change this.")
        else:
            await bot.say("No channel currently set. Use the `?set_daily_channel` command to change this.")

@bot.command(pass_context=True)
async def suggestion(ctx, *, string):
    """Sends a message to me with your suggestion!"""
    await bot.send_message(bot.procUser, "{0} says: ".format(ctx.message.author) + string)
    bot.say("Thanks for the suggestion!")

@bot.command(pass_context=True, name='3amerch', category='memes')
async def third_age_merch(ctx):
    """:("""
    if ctx.message.author == bot.procUser:
        await bot.say("-500m")
    else:
        await bot.say("!kms")

@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, the bot is cool.')

@cool.command(name='proc')
async def _proc():
    """Is proc cool?"""
    await bot.say('Yes, proc is cool.')


bot.loop.create_task(daily_message())
bot.run(config.token)

