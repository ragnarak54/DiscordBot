import discord
from discord.ext import commands
import random
import output
import datetime
import logging
import config

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)





description = '''A bot to help keep up with the Travelling Merchant's daily stock!.
There are a number of functionalities being worked on.'''
bot = commands.Bot(command_prefix='?', description=description)



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_at(message):

    await bot.process_commands(message)

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
    await bot.say(date_message)
    await bot.upload(output.output_img)

@bot.command(pass_context=True)
async def addnotif(ctx, item):
    """Adds an item to a user's notify list."""
    #playerNotifs = open("playerNotifs.txt", "w")
    await bot.say("Coming soon!")

@bot.command(name='3amerch', category='memes')
async def third_age_merch():
    """:("""
    await bot.say("-500m")

@bot.command()
async def donate():
    """Donation link"""

    await bot.say("https://www.paypal.me/ProcBot Any donation is greatly appreciated!")

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

bot.run(config.token)

