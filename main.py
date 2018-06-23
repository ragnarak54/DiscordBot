import discord
from discord.ext import commands
import random
import output
from datetime import timedelta
import datetime
import logging
import config
import userdb
import psycopg2
import asyncio
import request
import itemlist
import random
import merch
from fuzzywuzzy import process



logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''A bot to help keep up with the Travelling Merchant's daily stock!
Made by Proclivity. If you have any questions or want the bot on your server, pm me at ragnarak54#9413'''
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    appinfo = await bot.application_info()
    bot.procUser = appinfo.owner
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
        new_stock_string = "The new stock for {0} is out!\n".format(datetime.datetime.now().strftime("%m-%d-%Y"))

        data = userdb.ah_roles(items)
        roles = [role_tuple[0].strip() for role_tuple in data]  # get the roles for these items in AH discord
        # format the string to be sent
        b = [role + '\n' for role in roles]
        tag_string = "Tags: \n" + ''.join(b)
        ah_channel = bot.get_channel(config.ah_chat_id)
        await bot.send_file(ah_channel, output.output_img, content=new_stock_string + tag_string)

        # notify users for each item in today's stock
        for item in items:
            await auto_user_notifs(item)

        # get all the channels for daily messages, then loop through them to send messages
        channels = [bot.get_channel(channel_tuple[0].strip()) for channel_tuple in userdb.get_all_channels()]
        for channel in channels:
            await bot.send_file(channel, output.output_img, content=new_stock_string)

        await asyncio.sleep(60)

@bot.event
async def on_at(message):

    await bot.process_commands(message)

# ========= temp functions ========= #
@bot.command(pass_context=True)
async def daily_items(ctx, *, items):
    if ctx.message.author.id == config.proc or userdb.is_authorized(ctx.message.server, ctx.message.author):
        lst = [item.strip() for item in items.split(',')]
        item1 = merch.MerchItem(name=lst[0])
        item2 = merch.MerchItem(name=lst[1],)


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
    users = [user_tuple[0].strip() for user_tuple in data]
    for user in users:
        member = bot.get_server(userdb.user_server(user)).get_member(user_id=user)
        await bot.send_message(member, "{0} is in stock!".format(item))
        print(user)

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
async def notif_test(ctx):
    """Notifies users for today's stock"""
    if ctx.message.author.id == config.proc:
        items = [item.name.lower() for item in request.parse_merch_items()]
        print(items)
        for item in items:
            data = userdb.users(item)
            users = [user_tuple[0].strip() for user_tuple in data]
            print(users)
            for user in users:
                member = bot.get_server(userdb.user_server(user)).get_member(user_id=user)
                await bot.send_message(member, "{0} is in stock!".format(item))
    else:
        print("{0} tried to call notif_test!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call notif_test!".format(ctx.message.author))
        await bot.say("This command isn't for you!")

@bot.command(pass_context=True, name='merch', aliases=['merchant', 'shop', 'stock'])
async def merchant(ctx):
    """Displays the daily Traveling merchant stock."""
    now2 = datetime.datetime.today()
    if now2.day == int(request.parse_stock_date()):
        output.generate_merch_image()
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
                await bot.say("Don't forget to try out the new ?addnotif <item> function so you don't have to check the stock every day!")
    else:
        # await bot.say(
          #  "Due to technically problems with retrieving the daily stock, the ?merch command doesn't work. I hope to be"
           # " back in service tomorrow! Sorry for the inconvenience")
        # return
        await bot.say("The new stock isn't out yet!")

@bot.command(pass_context=True, aliases=['newnotif'])
async def addnotif(ctx, *, item):
    """Adds an item to a user's notify list."""
    stritem = str(item).lower()
    lst = [item.lower() for item in itemlist.item_list]
    results = get_matches(stritem, lst)
    print(results)
    if stritem not in lst:
        if results[0][1] - results[1][1] < 20:
            await bot.say("Make sure you're spelling your item correctly!\nCheck your PMs for a list of correct spellings, or refer to the wikia page.")
            b = [item + '\n' for item in itemlist.item_list]
            itemstrv2 = ''.join(b)
            await bot.send_message(ctx.message.author, 'Possible items:\n'+itemstrv2)
            return
    stritem = results[0][0]
    if not userdb.pref_exists(ctx.message.author.id, stritem):
        userdb.new_pref(ctx.message.author.id, ctx.message.author, stritem, ctx.message.server.id)
        await bot.say("Notification for {0} added!".format(stritem))
        print("{0} added notification for {1} in {2}".format(ctx.message.author, item, ctx.message.server))
    else:
        await bot.say("Already exists for this user")

def get_matches(query, choices, limit=3):
    results = process.extract(query, choices, limit=limit)
    return results

    #playerNotifs = open("playerNotifs.txt", "w")
    #await bot.say("Coming soon!")

@bot.command(pass_context=True, aliases=['delnotif', 'remnotif'])
async def removenotif(ctx, *, item):
    """Removes an item from a user's notify list."""
    stritem = str(item).lower()
    if not stritem.replace(' ', '').isalnum():
        await bot.say("Please enter the item in the proper format")
        return
    if userdb.pref_exists(ctx.message.author.id, stritem):
        userdb.remove_pref(ctx.message.author.id, stritem)
        await bot.say("Notification for {0} removed!".format(stritem))
    else:
        await bot.say("user does not have this preference")

@bot.command(pass_context=True)
async def shownotifs(ctx):
    """Shows a user's notify list"""
    data = userdb.user_prefs(ctx.message.author.id)
    if not data:
        await bot.say("No notifications added for this user")
        return
    notifs = [data_tuple[0].strip() for data_tuple in data]
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
    if ctx.message.author.id == config.proc:
        userdb.authorize_user(ctx.message.server, user)
        await bot.say("{0} authorized".format(user))
        print("{0} authorized".format(user))
    else:
        print("{0} tried to call authorize!".format(ctx.message.author))
        await bot.send_message(bot.procUser, "{0} tried to call authorize!".format(ctx.message.author))
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

@bot.command(name='3amerch', category='memes')
async def third_age_merch():
    """:("""
    await bot.say("-500m")

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

