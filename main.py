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


logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

userdb.create_table()



description = '''A bot to help keep up with the Travelling Merchant's daily stock!.
There are a number of functionalities being worked on.'''
bot = commands.Bot(command_prefix='?', description=description)



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

async def daily_message():
    await bot.wait_until_ready()
    while not bot.is_closed:
        now = datetime.datetime.now()
        schedule_time = now.replace(hour=0, minute=2) + timedelta(days=1)
        time_left = schedule_time - now
        sleep_time = time_left.total_seconds()
        print(sleep_time)
        await asyncio.sleep(sleep_time)
        now2 = datetime.datetime.now()
        while not now2.day == request.parse_stock_date():
            await asyncio.sleep(60)
        items = [item.name.lower() for item in request.parse_merch_items()]
        data = userdb.ah_roles(items)
        roles = [role_tuple[0].strip() for role_tuple in data]
        b = [role + '\n' for role in roles]
        tag_string = "Tags: \n" + ''.join(b)
        await bot.send_message(discord.Object(id=config.ah_chat_id), tag_string)
        auto_user_notifs()
        output.generate_merch_image()
        channel = discord.Object(id=config.chat_id)
        await bot.send_file(channel, output.output_img, content="Today's stock:")

        await asyncio.sleep(60)





@bot.event
async def on_at(message):

    await bot.process_commands(message)

async def auto_user_notifs(item):
    data = userdb.users(item)
    users = [user_tuple[0].strip() for user_tuple in data]
    for user in users:
        member = bot.get_server(userdb.user_server(user)).get_member(user_id=user)
        await bot.send_message(member, "{0} is in stock!".format(item))
        print(user)

@bot.command(pass_context=True, name='ah_merch')
async def ah_test(ctx):
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
    """Displays users who have the input preference"""
    if ctx.message.author.id == config.proc:
        data = userdb.users(item)
        users = [user_tuple[0].strip() for user_tuple in data]
        for user in users:
            print(user)
            member = bot.get_server(userdb.user_server(user)).get_member(user_id=user)
            await bot.send_message(member, "{0} is in stock!".format(item))
            print(user)

@bot.command(pass_context=True)
async def notif_test(ctx):
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

@bot.command(pass_context=True, name='merch', aliases=['merchant', 'shop', 'stock'])
async def merchant(ctx):
    """Displays the daily Traveling merchant stock."""
    output.generate_merch_image()
    now = datetime.datetime.now()
    member = ctx.message.author
    channel = ctx.message.channel
    server = ctx.message.server
    logger.info("called at " + now.strftime("%H:%M") + ' by {0} in {1} of {2}'.format(member,channel,server))
    print("called at " + now.strftime("%H:%M") + ' by {0} in {1} of {2}'.format(member,channel,server))
    date_message = "The stock for " + now.strftime("%d-%m-%Y") + ":"
    await bot.send_file(ctx.message.channel, output.output_img, content=date_message)

@bot.command(pass_context=True)
async def addnotif(ctx, *, item):
    """Adds an item to a user's notify list."""
    stritem = str(item).lower()
    if not stritem.replace(' ', '').isalnum():
        await bot.say("lul")
        return
    if not userdb.pref_exists(ctx.message.author.id, stritem):
        userdb.new_pref(ctx.message.author.id, ctx.message.author, stritem, ctx.message.server.id)
        await bot.say("Notification for {0} added!".format(item))
    else:
        await bot.say("Already exists for this user")


    #playerNotifs = open("playerNotifs.txt", "w")
    #await bot.say("Coming soon!")

@bot.command(pass_context=True)
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
    """Shows a user's preferences"""
    data = userdb.user_prefs(ctx.message.author.id)
    notifs = [data_tuple[0].strip() for data_tuple in data]
    if not data:
        await bot.say("No notifications added for this user")
        return
    notifs = [data_tuple[0].strip() for data_tuple in data]
    b = [':small_blue_diamond:' + x + '\n' for x in notifs]
    user_string = 'Current notifications for {0}:\n'.format(ctx.message.author.nick)
    string = user_string + ''.join(b)
    await bot.say(string)


@bot.command(pass_context=True)
async def test(ctx, item):
    userdb.pref_exists(ctx.message.author.id, item)


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

@bot.command()
async def testme():
    userdb.test_connection()

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

