import asyncio
import asyncpg
import datetime
import logging
import random
from datetime import timedelta

import config
import discord
from discord import app_commands
from discord.ext import commands
from discord import app_commands

from cogs import error_handler, notifs, server_management, stock, world_tracker, notifs_legacy, analytics
import itemlist
import items as it
import merch
import output
import userdb
from cogs.notifs import get_matches


logger = logging.getLogger('discord')
logger.setLevel(logging.CRITICAL)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''```A bot to help keep up with the Travelling Merchant's daily stock!
Made by Proclivity. If you have any questions or want the bot on your server, pm me at ragnarak54#9413.
Lets get started!\n\n'''

discord.http._set_api_version(9)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=['?', '!'], description=description, intents=intents)
bot.remove_command("help")


daily_messages = []
skip_daily = False


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
async def on_guild_join(guild: discord.Guild):
    try:
        owner = await guild.fetch_member(guild.owner_id)
        if not await bot.db.is_authorized(owner):
            await bot.db.authorize_user(owner)
        await bot.procUser.send(f"Bot joined `{guild.name}`.")
        len([x for x in bot.users if not x.bot])
        for channel in [x for x in guild.text_channels]:
            if channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).embed_links:
                em = discord.Embed(title="Travelling Merchant Bot",
                                   description="Thanks for inviting me! You can find a list of my commands [here]"
                                               "(https://github.com/ragnarak54/DiscordBot/blob/master/README.md). "
                                   f"By default your server's owner {owner.mention} has the power to "
                                   f"set a daily message channel for the new stock. See the command list for more "
                                   f"options and info!")
                em.set_footer(text="Made by ragnarak54#9413")
                await channel.send(embed=em)
                break

    except Exception as e:
        await bot.procUser.send(f"Error when joining {guild.name}: {e}")
        for channel in [x for x in guild.text_channels]:
            if channel.permissions_for(guild.me).send_messages:
                print(channel.permissions_for(guild.me).read_messages)
                await channel.send("Something went wrong during my setup! Try reinviting me, or message my owner "
                                   "@ragnarak54#9413 if the issue persists!")


@bot.event
async def on_guild_remove(guild: discord.Guild):
    # TODO post member intent approval uncomment
    # owner = await guild.fetch_member(guild.owner_id)
    # await bot.db.unauthorize_user(owner)
    # await bot.procUser.send(f"Left guild {guild.name}, which had `{len(guild.members)}` members. "
    #                         f"New usercount `{len([x for x in bot.users if not x.bot])}`.")
    await bot.procUser.send(f"Left guild `{guild.name}`")


@bot.command()
async def user_count(ctx):
    m = 0
    for guild in bot.guilds:
        m += guild.member_count
    await ctx.send(f"users: {m}")


@owner_check()
@bot.command()
async def skip_next_daily(ctx):
    global skip_daily
    skip_daily = not skip_daily
    await ctx.send(f"skip_daily now `{skip_daily}`")


@owner_check()
@bot.command()
async def custom_stock(ctx, *items):
    stock = []
    print(items)
    if items[0] == 'normal':
        output.generate_merch_image()
        output.generate_merch_image(1)

        await send_stock(merch.get_stock())
        return
    lst = [item for item in itemlist.item_list]
    if any([x not in lst for x in items]):
        await ctx.send("Try typing that out again!")
        return
    if len(items) == 3:
        stock.append(
            merch.MerchItem('Uncharted island map (Deep Sea Fishing).png', 'Uncharted island map', '800,000', 1,
                            "Allows travel to an [[uncharted island]] with the chance of 3-6 special resources at the cost "
                            "of no supplies<br />In addition, players may also rarely receive a [[Uncharted island map ("
                            "red)|red uncharted island map]].", "<:Uncharted_map:755960222949965825>"))
    for item in items:
        stock.append(merch.MerchItem(f'{item}.png', item, *it.get_attrs(item)))
    dsf_embed = output.generate_merch_embed(items=stock, dsf=True)
    dsf_embed.description += f'\n{bot.get_channel(789279009333575700).mention} for worlds, or join **WhirlpoolDnD** FC!'
    general_embed = output.generate_merch_embed(items=stock)
    await ctx.send("About to send the following stock, confirm?", embed=dsf_embed)
    msg = await ctx.send(embed=general_embed)
    await msg.add_reaction('\U00002705')

    def check(reaction, user):
        return user == ctx.message.author and reaction.message == msg and reaction.emoji == '\U00002705'

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Aborted")
    else:
        await ctx.send("Confirmed, sending stock (jk)")

    output.generate_merch_image(items=stock)
    await send_stock(stock, send_dsf=True)


@bot.command()
async def dsf_merch(ctx):
    if (await bot.db.is_authorized(ctx.author) and ctx.guild.id == 420803245758480405) or await bot.is_owner(ctx.author):
        items = [item.name.lower() for item in merch.get_stock()]
        dsf_roles = [role_tuple[0].strip() for role_tuple in await bot.db.dsf_roles(items)]
        tag_string = ""
        if dsf_roles:
            tag_string = " ".join(dsf_roles)
        try:
            em = output.generate_merch_embed(dsf=True)
            em.description += f'\n{bot.get_channel(789279009333575700).mention} for worlds, or join **WhirlpoolDnD** FC!'
            await ctx.send(tag_string, embed=em)
        except Exception as e:
            await bot.procUser.send(f"Couldn't send message to DSF: {e}")
    else:
        await bot.procUser.send(f"{ctx.author} tried to call dsf_merch in {ctx.guild}!")


# background task for automatic notifications each day
async def daily_message():
    global skip_daily
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.datetime.now()
        schedule_time = now.replace(hour=0, minute=1) + timedelta(days=1)
        time_left = schedule_time - now
        sleep_time = time_left.total_seconds()  # seconds from now until tomorrow at 00:01
        print(sleep_time)
        await asyncio.sleep(sleep_time)
        if skip_daily:
            await bot.procUser.send("Skipping daily message")
            skip_daily = False
        else:
            output.generate_merch_image()  # generate the new image for today and tomorrow
            output.generate_merch_image(1)

            await send_stock(merch.get_stock())

        await asyncio.sleep(60)

# careful with custom stock, will still generate the "tomorrow's stock" text in the embed
async def send_stock(stock, send_dsf=True):
    items = [item.name.lower() for item in stock]
    new_stock_string = "The new stock for {0} is out!\n".format(datetime.datetime.now().strftime("%m/%d/%Y"))
    try:
        if send_dsf:
            dsf_roles = [role_tuple[0].strip() for role_tuple in await bot.db.dsf_roles(items)]
            tag_string = " ".join(dsf_roles)

            dsf_channel = bot.get_channel(config.dsf_chat_id)
            em = output.generate_merch_embed(items=stock, dsf=True)
            em.description += f'\n{bot.get_channel(789279009333575700).mention} for worlds, or join **WhirlpoolDnD** FC!'
            await dsf_channel.send(tag_string, embed=em)
    except Exception as e:
        await bot.procUser.send(f"Couldn't send message to DSF: {e}")

    data = await bot.db.ah_roles(items)
    roles = set([role_tuple[0].strip() for role_tuple in data])  # get the roles for these items in AH discord

    # format the string to be sent
    tag_string = ""
    if roles != set([]):
        b = [role + '\n' for role in roles]
        tag_string = "Tags: \n" + ''.join(b)
    try:
        ah_channel = bot.get_channel(config.ah_chat_id)
        await ah_channel.send(file=discord.File(output.today_img), content=new_stock_string + tag_string)
    except Exception as e:
        await bot.procUser.send(f"Couldn't send message to AH: {e}")

    # notify users for each item in today's stock
    for item in items:
        await auto_user_notifs(item)

    # get all the channels for daily messages, then loop through them to send messages
    # also, store them in daily_messages in case of a bad update
    daily_messages.clear()
    # TODO update DB table
    channels = await bot.db.get_all_channels()
    for channel in channels:
        try:
            daily_messages.append(await channel.send(embed=output.generate_merch_embed(items=stock)))

            tag = channel.guild.get_role(await bot.db.get_tag(channel.guild))
            # daily_messages.append(await channel.send(file=discord.File(output.today_img),
            #                                        content=new_stock_string if not tag else new_stock_string + tag.mention))
        except discord.Forbidden or Exception:
            print(f'cant send message to {channel.name} of {channel.guild.name}')


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
    if await bot.db.is_authorized(ctx.author) or ctx.author == await bot.is_owner(ctx.author):
        new_toggle_state = await bot.db.toggle(ctx)
        if not new_toggle_state:
            await ctx.send("Daily messages toggled off")
        else:
            current = await bot.db.current_channel(ctx.guild)
            await ctx.send(
                f"Daily messages toggled on. Current channel is {current.mention}")
    else:
        print(f"{ctx.author} tried to call toggle_daily!")
        await bot.procUser.send(f"{ctx.author} tried to call toggle_daily!")
        await ctx.send("You aren't authorized to do that. If there's been a mistake send me a PM!")


# PMs users who have the item preference
# TODO holy god fix it
async def auto_user_notifs(item):
    data = await bot.db.users(item)  # user ids
    userlist = []
    for user_tuple in data:
        user = await bot.fetch_user(user_tuple[0])
        if user is None:
            print(f"{user_tuple[0]} wasn't found! pref for {item} removed")
            try:
                await bot.db.remove_pref(user_tuple[0], item)
            except Exception as e:
                print("you failed: ", e)
        else:
            userlist.append(user)
    print(f"{len(userlist)} users for {item}")
    for user in userlist:
        try:
            if item == "uncharted island map":
                await user.send(embed=output.generate_merch_embed())
            else:
                await user.send(f"{item} is in stock!")
        except discord.Forbidden:
            print(f"forbidden: cannot send message to {user}")
        except:
            pass


@bot.command(name='ah_merch')
async def ah_test(ctx):
    """Tags the relevant roles in AH discord for the daily stock"""
    if ctx.author.top_role >= discord.utils.get(ctx.guild.roles, id=config.ah_mod_role) \
            or ctx.author == bot.procUser:
        items = [item.name.lower() for item in merch.get_stock()]
        data = await bot.db.ah_roles(items)
        roles = [role_tuple[0].strip() for role_tuple in data]
        b = [role + '\n' for role in roles]
        tag_string = "Tags: " + ''.join(b)
        await bot.get_channel(config.ah_chat_id).send(content=tag_string, file=discord.File(output.today_img))


@bot.command()
@owner_check()
async def user_notifs(ctx, *, item):
    """Notifies users who have the input preference"""
    data = await bot.db.users(item)
    users = [await bot.fetch_user(user_tuple[0]) for user_tuple in data]
    for user in users:
        print(user)
        await user.send(f"{item} is in stock!")


@bot.command()
@owner_check()
async def force_notifs(ctx):
    """Notifies users for today's stock"""
    items = [item.name.lower() for item in merch.get_stock()]
    for item in items:
        await auto_user_notifs(item)


@bot.command(name='merch', aliases=['merchant', 'shop', 'stock'])
async def merchant(ctx):
    """Displays the daily Traveling merchant stock."""
    now = datetime.datetime.now()
    member = ctx.author
    channel = ctx.channel
    guild = ctx.guild
    print(f'called at {now.strftime("%H:%M")} by {member} in {channel} of {guild}')
    await ctx.send(embed=output.generate_merch_embed(worlds=bot.get_cog('WorldTracker').worlds))
    if not await bot.db.user_exists(ctx.author.id):
        print(f"user {ctx.author} doesn't have any preferences")
        chance = random.random()
        if chance < 0.1:
            await ctx.send("Don't forget to try out the ?addnotif <item> function so you don't "
                           "have to check the stock every day!")


@bot.command(aliases=['tmrw', 'tommorow'])
async def tomorrow(ctx):
    await ctx.send(embed=output.generate_merch_embed(1))


@bot.command()
async def future(ctx, days: int):
    assert days > 0, "Negative days entered"
    await ctx.send(embed=output.generate_merch_embed(days))


@bot.command(name="next")
async def _next(ctx, *, item):
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


@bot.command(aliases=['world'])
async def worlds(ctx):
    w = bot.get_cog('WorldTracker').worlds
    if w:
        await ctx.send(f"Current world(s): {', '.join([f'**{_}**' for _ in w])}")
    else:
        await ctx.send("No current worlds")


# TODO make userdb do id->object
@bot.command(aliases=["fix_daily_messages"])
async def fix_daily_message(ctx, send_dsf=False):
    if ctx.author == bot.procUser:
        await send_stock(merch.get_stock(), send_dsf=send_dsf)
    else:
        await bot.procUser.send(f"{ctx.author} tried to call fix daily messages!")


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
    channels = await bot.db.get_all_channels()
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
    all_users = [x for x in await bot.db.get_all_users() if x]
    for user in all_users:
        try:
            await user.send(string)
        except discord.Forbidden:
            print(f"cant send message to {user}")


@bot.command()
async def users(ctx, *, item):
    if ctx.author == bot.procUser:
        userlist = [await bot.fetch_user(x) for x in await bot.db.users(item)]
        await ctx.send(userlist)


@bot.command()
async def authorize(ctx, user: discord.Member):
    if ctx.author == bot.procUser or await bot.db.is_authorized(ctx.author):
        if not await bot.db.is_authorized(user):
            await bot.db.authorize_user(user)
            await ctx.send(f"{user} authorized")
            print(f"{user} authorized")
        else:
            await ctx.send(f"{user} is already authorized")
    else:
        print(f"{ctx.author} tried to call authorize!")
        await bot.procUser.send(f"{ctx.author} tried to call authorize!")
        owner = await ctx.guild.fetch_member(ctx.guild.owner_id)
        await ctx.send(f"You aren't authorized to do that. Owner {owner.mention} is authorized by default, "
                       f"and can authorize others. If there's been a mistake send @ragnarak54#9413 a PM!")


@bot.command()
async def unauthorize(ctx, user: discord.Member):
    if ctx.author == bot.procUser:
        if await bot.db.is_authorized(user):
            await bot.db.unauthorize_user(user)
            await ctx.send(f"{user} unauthorized.")
        else:
            await ctx.send(f"{user} isn't authorized")
    else:
        print(f"{ctx.author} tried to call unauthorize!")
        await bot.procUser.send(f"{ctx.author} tried to call unauthorize!")
        await ctx.author("You aren't authorized to do that. If there's been a mistake send me a PM!")


@bot.command()
async def set_daily_channel(ctx, new_channel: discord.TextChannel):
    """A command for authorized users to set or update the channel that receives the daily stock message"""
    perms = new_channel.permissions_for(ctx.guild.me)
    # use_external_emojis
    # send_messages
    # embed_links
    if not (perms.use_external_emojis and perms.send_messages and perms.embed_links):
        try:
            await ctx.message.add_reaction('\U0000274c')
        except:
            pass
        await ctx.send(f"Insufficient permissions to send to {new_channel.mention}: "
                       f"need `send messages`, `use external emojis`, and `embed links`.")
        return
    new = await bot.db.set_channel(new_channel)
    if new:
        await ctx.send(f"Daily message channel set to {new_channel.mention}")
    else:
        await ctx.send(f"Daily message channel updated to {new_channel.mention}")


@bot.command(aliases=['channel', 'current_channel'])
async def daily_channel(ctx):
    channel = await bot.db.current_channel(ctx.guild)
    if channel is not None:
        await ctx.send(f"Currently set to {channel.mention}.\nUse the `?set_daily_channel` command to "
                       f"change this.")
    else:
        await ctx.send("No channel currently set. Use the `?set_daily_channel` command to change this.")


@bot.command()
async def daily_tag(ctx, role: discord.Role = None):
    if not role:
        tag = await bot.db.get_tag(ctx.guild)
        if tag:
            tag = ctx.guild.get_role(tag)
            await ctx.send(f"The {tag.name} role is currently set as your daily tag role")
        else:
            await ctx.send(f"Your server doesn't currently have a daily tag role. Set one with `?daily_tag @role`.")
        return
    try:
        await bot.db.add_role_tag(ctx.guild, role)
    except Exception as e:
        await ctx.send(f"Couldn't set daily tag role: {e}")
        return
    await ctx.send(f"Successfully updated daily role tag to `{role.name}` for {ctx.guild.name}")


@bot.command()
async def clear_worlds(ctx):
    if await bot.db.is_authorized(ctx.author) or ctx.author == bot.procUser:
        bot.get_cog('WorldTracker').worlds.clear()
        await ctx.send('World queue cleared')


@commands.cooldown(1, 15, commands.BucketType.member)
@bot.command()
async def moose(ctx):
    await ctx.send(await bot.db.get_moose())


@bot.command()
async def add_moose(ctx, url=None):
    if await bot.db.is_mooser(ctx.author):
        await bot.db.add_moose(url)
        try:
            await ctx.message.add_reaction('\U00002705')
        except:
            pass
        await ctx.send(f'`{url}` added')


@bot.command()
async def delete_moose(ctx, url):
    if await bot.db.is_mooser(ctx.author):
        await bot.db.delete_moose(url)
        try:
            await ctx.message.add_reaction('\U00002705')
        except:
            pass
        await ctx.send(f'`{url}` deleted')


@bot.command()
async def add_mooser(ctx, member: discord.Member):
    if await bot.db.is_mooser(member):
        await bot.db.add_mooser(member)
        try:
            await ctx.message.add_reaction('\U00002705')
        except:
            pass


@bot.command()
async def remove_mooser(ctx, member: discord.Member):
    if bot.db.is_mooser(member):
        await bot.db.remove_mooser(member)
        try:
            await ctx.message.add_reaction('\U00002705')
        except:
            pass


@bot.command()
async def suggestion(ctx, *, string):
    """Sends a message to me with your suggestion!"""
    await bot.procUser.send(f"{ctx.author} says: {string}")
    await ctx.send("Thanks for the suggestion!")


@bot.command(aliases=['splits'])
async def split(ctx, price, percent_tip: int = 1):
    try:
        price = price.replace('m', '').replace(',', '')
        price = float(price)
        if len(str(int(price))) == 9:
            price /= 1000000
        elif len(str(int(price))) != 3:
            raise ValueError
        tip = price * (percent_tip / 100)
        to_split = (price - 2 * tip) / 7
        base_hammer = to_split + tip
        await ctx.send(f"*{percent_tip}% tip splits:*\n"
                       f"Base/hammer: {round(base_hammer, 2)}m\nOthers: {round(to_split, 2)}m")
    except ValueError:
        await ctx.send("Something's wrong with your input! Expected format is `?split 545.2`")


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
        if "proc" in choice and random.randint(1, 10) > 2:
            await ctx.send(choice)
            return
        if "nex" in choice and random.randint(1, 10) > 3:
            await ctx.send(choice)
            return
        if "kk" in choices and random.randint(1, 10) > 2:
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


@bot.command()
@owner_check()
async def pyval(ctx, *, expr):
    env = {
        'ctx': ctx,
        'bot': bot,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
        'discord': discord
    }
    try:
        ret = eval(expr, env)
    except Exception as e:
        ret = e
    await ctx.send(ret)


@bot.check
def check_channel(ctx):
    return ctx.channel.id != 523161748866596884


@owner_check()
@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send(f"synced commands")


async def main():
    async with bot:
        await bot.add_cog(error_handler.CommandErrorHandler(bot))
        bot.pool = await asyncpg.create_pool(config.psql)
        bot.db = userdb.DB(bot)
        await bot.add_cog(notifs.Notifications(bot))
        await bot.add_cog(stock.Stock(bot))
        await bot.add_cog(world_tracker.WorldTracker(bot))
        await bot.add_cog(server_management.ServerManagement(bot))
        await bot.add_cog(notifs_legacy.NotificationsLegacy(bot))
        await bot.add_cog(analytics.Analytics(bot))

        bot.daily_background = bot.loop.create_task(daily_message())
        await bot.start(config.token)

asyncio.run(main())
