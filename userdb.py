import config
import discord
from discord.ext import commands


# noinspection SqlResolve
class DB(commands.Cog):
    def __init__(self, bot):
        self.conn = bot.pool
        self.bot = bot

    async def new_pref(self, author, item):
        await self.conn.execute("insert into user_prefs values ($1, $2, $3, $4)", str(author.id), str(author), item,
                                "direct message" if not isinstance(author, discord.Member) else str(author.guild.id))

    async def remove_pref(self, userID, item):
        await self.conn.execute("delete from user_prefs where item=$1 and discordID=$2", item, str(userID))

    async def pref_exists(self, userID, item):
        results = await self.conn.fetchrow("select exists(select 1 from user_prefs where discordID = $1 and item = $2)",
                                        str(userID), str(item))
        return results[0]

    async def user_prefs(self, userID):
        return await self.conn.fetch("select item from user_prefs where discordID = $1", str(userID))

    async def users(self, item):
        return await self.conn.fetch("SELECT DISTINCT discordID from user_prefs WHERE item = $1", str(item))

    async def user_server(self, userID) -> str:
        results = await self.conn.fetchrow("SELECT DISTINCT server from user_prefs WHERE discordID = $1", str(userID))
        return results[0].strip()

    async def user_exists(self, userID) -> bool:
        result = await self.conn.fetchrow("select exists(select 1 from user_prefs where discordID = $1)", str(userID))
        return result[0]

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
        return await self.conn.fetchrow(
            "select exists(select 1 from authorized_users where guild_id=$1 and user_id=$2)",
            user.guild.id, user.id)

    async def set_channel(self, channel: discord.TextChannel) -> bool:
        """"Returns False if updating channel, True if new server"""
        new = await self.conn.fetchrow("select exists(select 1 from daily_message_channels where guild_id=$1)",
                                       channel.guild.id)
        if new:
            await self.conn.execute(
                "insert into daily_message_channels (guild_id, guild_name, channel_id) values ($1, $2, $3)",
                channel.guild.id, channel.guild.name, channel.id)
        else:
            await self.conn.execute("update daily_message_channels set channel_id=$1 where guild_id=$2",
                                    channel.id, channel.guild.id)
        return new

    async def toggle(self, ctx):
        """Returns False if toggled off successfully, returns daily channel if toggled on"""
        new = await self.conn.fetchrow("select exists(select 1 from daily_message_channels where guild_id=$1)",
                                       ctx.guild.id)
        if new:
            await self.set_channel(ctx.channel)
            return ctx.channel
        on_off = await self.conn.fetchrow("select toggle from daily_message_channels where server_id=$1", ctx.guild.id)
        await self.conn.execute("update daily_message_channels set toggle=$1", not on_off)
        return not on_off

    async def current_channel(self, server: discord.Guild) -> discord.TextChannel:
        return self.bot.get_channel(
            await self.conn.fetchrow("select channel_id from daily_message_channels where guild_id=$1", server.id))

    async def get_all_channels(self):
        return [self.bot.get_channel(x[0]) for x in
                await self.conn.fetch("select channel_id from daily_message_channels where toggle=true")]

    async def get_all_users(self):
        return [self.bot.get_user(int(x[0])) for x in
                await self.conn.fetch("select distinct discordid from user_prefs")]

    async def get_id_table(self):
        return await self.conn.fetch("select origin_id, monitor_id from monitor_mappings")

    async def insert_new_mapping(self, origin: int, name: str, mapping: int):
        return await self.conn.execute("insert into monitor_mappings values ($1, $2, $3)", origin, name, mapping)

    async def remove_mapping(self, origin: int):
        return await self.conn.execute("delete from monitor_mappings where origin_id=$1", origin)

    async def add_role_tag(self, server: discord.Guild, tag: discord.Role):
        new = await self.conn.fetchrow("select exists(select 1 from daily_message_channels where guild_id=$1)",
                                       server.id)
        if new:
            await self.conn.execute(
                "insert into daily_message_channels (guild_id, guild_name, daily_role_id) values ($1, $2, $3)",
                server.id, server.name, tag.id)
        else:
            await self.conn.execute("update daily_message_channels set daily_role_id=$1 where guild_id=$2", tag.id,
                                    server.id)
        return new
