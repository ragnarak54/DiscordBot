import datetime
import config
import discord
from discord.ext import commands


# noinspection SqlResolve
class DB(commands.Cog):
    def __init__(self, bot):
        self.conn = bot.pool
        self.bot = bot

    async def new_pref(self, author, item):
        print(author.id)
        await self.conn.execute("insert into user_prefs values ($1, $2, $3, $4)", author.id, str(author), item,
                                0 if not isinstance(author, discord.Member) else author.guild.id)

    async def remove_pref(self, userID, item):
        await self.conn.execute("delete from user_prefs where item=$1 and user_id=$2", item, userID)

    async def pref_exists(self, userID, item):
        results = await self.conn.fetchrow("select exists(select 1 from user_prefs where user_id = $1 and item = $2)",
                                           userID, str(item))
        return results[0]

    async def user_prefs(self, author):
        results = await self.conn.fetch("select item from user_prefs where user_id = $1", author.id)
        return [data_tuple[0].strip() for data_tuple in results]

    async def users(self, item):
        return await self.conn.fetch("SELECT DISTINCT user_id from user_prefs WHERE item = $1", str(item))

    async def user_server(self, userID) -> str:
        results = await self.conn.fetchrow("SELECT DISTINCT server from user_prefs WHERE user_id = $1", userID)
        return results[0].strip()

    async def user_exists(self, userID) -> bool:
        result = await self.conn.fetchrow("select exists(select 1 from user_prefs where user_id = $1)", userID)
        return result[0]

    async def dsf_roles(self, items):
        items = [item.lower() for item in items]
        roles = []
        for item in items:
            role = await self.conn.fetchrow("select role from dsf_roles where item = $1", item)
            print(item, role)
            if role and role not in roles:
                roles.append(role)
        return roles


    async def ah_roles(self, items):
        items = [item.lower() for item in items][1:]
        return await self.conn.fetch("SELECT role from ah_roles where (item = $1 or item = $2 or item = $3)", *items)

    # disallow double authorizations
    async def authorize_user(self, user: discord.Member):
        attrs = [user.guild.id, user.guild.name, user.id, str(user)]
        return await self.conn.execute("INSERT INTO authorized_users values ($1, $2, $3, $4)", *attrs)

    async def unauthorize_user(self, user: discord.Member):
        return await self.conn.execute("delete from authorized_users where guild_id=$1 and user_id=$2",
                                       user.guild.id, user.id)

    async def is_authorized(self, user: discord.Member):
        if user == self.bot.procUser:
            return True
        r = await self.conn.fetchrow(
            "select exists(select 1 from authorized_users where guild_id=$1 and user_id=$2)",
            user.guild.id, user.id)
        return r[0]

    async def set_channel(self, channel: discord.TextChannel) -> bool:
        """"Returns False if updating channel, True if new server"""
        r = await self.conn.fetchrow("select exists(select 1 from daily_message_channels where guild_id=$1)",
                                     channel.guild.id)
        new = not r[0]
        if new:
            await self.conn.execute(
                "insert into daily_message_channels (guild_id, guild_name, channel_id, toggle) values ($1, $2, $3, $4)",
                channel.guild.id, channel.guild.name, channel.id, True)
        else:
            await self.conn.execute("update daily_message_channels set channel_id=$1 where guild_id=$2",
                                    channel.id, channel.guild.id)
        return new

    async def toggle(self, ctx):
        """Returns False if toggled off successfully, returns daily channel if toggled on"""
        r = await self.conn.fetchrow("select exists(select 1 from daily_message_channels where guild_id=$1)",
                                     ctx.guild.id)
        new = not r[0]
        if new:
            await self.set_channel(ctx.channel)
            return ctx.channel
        r = await self.conn.fetchrow("select toggle from daily_message_channels where guild_id=$1", ctx.guild.id)
        on_off = r[0]
        await self.conn.execute("update daily_message_channels set toggle=$1 where guild_id=$2", not on_off,
                                ctx.guild.id)
        return not on_off

    async def current_channel(self, server: discord.Guild) -> discord.TextChannel:
        r = await self.conn.fetchrow("select channel_id from daily_message_channels where guild_id=$1", server.id)
        return None if not r else self.bot.get_channel(r[0])

    async def get_all_channels(self):
        fetched = await self.conn.fetch("select channel_id from daily_message_channels where toggle=true")
        channels = []
        for id_tup in fetched:
            channel = self.bot.get_channel(id_tup[0])
            if channel:
                channels.append(channel)
            else:
                # delete channel id row from table
                try:
                    await self.conn.execute("delete from daily_message_channels where channel_id=$1", id_tup[0])
                except:
                    pass
                await self.bot.procUser.send(f"Couldn't fetch channel id {id_tup[0]}, deleting!")
        return channels

    async def get_all_users(self):
        return [await self.bot.fetch_user(int(x[0])) for x in
                await self.conn.fetch("select distinct user_id from user_prefs")]

    async def get_id_table(self):
        return await self.conn.fetch("select origin_id, monitor_id from monitor_mappings")

    async def insert_new_mapping(self, origin: int, name: str, mapping: int):
        return await self.conn.execute("insert into monitor_mappings values ($1, $2, $3)", origin, name, mapping)

    async def remove_mapping(self, origin: int):
        return await self.conn.execute("delete from monitor_mappings where origin_id=$1", origin)

    async def add_role_tag(self, server: discord.Guild, tag: discord.Role):
        r = await self.conn.fetchrow("select exists(select 1 from daily_message_channels where guild_id=$1)",
                                     server.id)
        new = not r[0]
        if new:
            await self.conn.execute(
                "insert into daily_message_channels (guild_id, guild_name, daily_role_id) values ($1, $2, $3)",
                server.id, server.name, tag.id)
        else:
            await self.conn.execute("update daily_message_channels set daily_role_id=$1 where guild_id=$2", tag.id,
                                    server.id)
        return new

    async def get_tag(self, server):
        tag = await self.conn.fetchrow("select daily_role_id from daily_message_channels where guild_id=$1", server.id)
        return tag if not tag else tag[0]

    async def add_mooser(self, user: discord.Member):
        await self.conn.execute("insert into moosers (name, user_id) values ($1, $2)", user.name, user.id)

    async def remove_mooser(self, user: discord.Member):
        return await self.conn.execute("delete from moosers where user_id=$1", user.id)

    async def is_mooser(self, user: discord.Member):
        if user == self.bot.procUser:
            return True
        r = await self.conn.fetchrow(
            "select exists(select 1 from moosers where user_id=$1)", user.id)
        return r[0]

    async def add_moose(self, url):
        await self.conn.execute("insert into moose_pics (url) values ($1)", url)

    async def get_moose(self):
        moose = await self.conn.fetchrow("select url from moose_pics order by random() limit 1")
        return moose[0]

    async def delete_moose(self, url):
        await self.conn.execute("delete from moose_pics where url=$1", url)

    async def log_command(self, name: str, guild_id: int, caller_id: int, type: str):
        await self.conn.execute("insert into command_calls (name, guild_id, user_id, type, timestamp)"
                                " values ($1, $2, $3, $4, $5)", name, guild_id, caller_id, type, datetime.datetime.now())
