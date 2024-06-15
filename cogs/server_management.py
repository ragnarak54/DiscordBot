import typing

import discord
from discord.ext import commands
from discord import app_commands


class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="toggle_daily")
    async def toggle_daily(self, interaction: discord.Interaction):
        """Toggles the daily stock message on or off for your server"""
        if await self.bot.db.is_authorized(interaction.user):
            new_toggle_state = await self.bot.db.toggle(interaction)
            if not new_toggle_state:
                await interaction.response.send_message("Daily messages toggled off")
            else:
                current = await self.bot.db.current_channel(interaction.guild)
                await interaction.response.send_message(
                    f"Daily messages toggled on. Current channel is {current.mention}")
        else:
            await self.bot.procUser.send(f"{interaction.user} tried to call toggle_daily!")
            await interaction.response.send_message("You aren't authorized to do that. If there's been a mistake send me a PM!",
                                                    ephemeral=True)

    @app_commands.command(name="authorize")
    async def authorize(self, interaction: discord.Interaction, user: discord.Member):
        """Authorizes a user to manage daily messages in your server"""
        if await self.bot.db.is_authorized(interaction.user):
            if not await self.bot.db.is_authorized(user):
                await self.bot.db.authorize_user(user)
                await interaction.response.send_message(f"{user} authorized")
                print(f"{user} authorized")
            else:
                await interaction.response.send_message(f"{user} is already authorized")
        else:
            print(f"{interaction.user} tried to call authorize!")
            await self.bot.procUser.send(f"{interaction.user} tried to call authorize!")
            owner = await interaction.guild.fetch_member(interaction.guild.owner_id)
            await interaction.response.send_message(f"You aren't authorized to do that. Owner {owner.mention} is "
                                                    f"authorized by default, and can authorize others. If there's "
                                                    f"been a mistake send @ragnarak54#9413 a PM!", ephemeral=True)

    @app_commands.command(name="unauthorize")
    async def unauthorize(self, interaction: discord.Interaction, user: discord.Member):
        if await self.bot.is_owner(interaction.user):
            if await self.bot.db.is_authorized(user):
                await self.bot.db.unauthorize_user(user)
                await interaction.response.send_message(f"{user} unauthorized.")
            else:
                await interaction.response.send_message(f"{user} isn't authorized")
        else:
            print(f"{interaction.user} tried to call unauthorize!")
            await self.bot.procUser.send(f"{interaction.user} tried to call unauthorize!")
            await interaction.response.send_message(
                "You aren't authorized to do that. If there's been a mistake send me a PM!", ephemeral=True)

    @app_commands.command(name="set_daily_channel")
    async def set_daily_channel(self, interaction: discord.Interaction, new_channel: discord.TextChannel):
        """A command for authorized users to set or update the channel that receives the daily stock message"""
        perms = new_channel.permissions_for(interaction.guild.me)
        if not (perms.use_external_emojis and perms.send_messages and perms.embed_links):
            await interaction.response.send_message(f"⚠️ Missing permissions for {new_channel.mention}. I'll need "
                                                    f"`send messages`, `use external emojis`, and `embed links`.")
            return
        new = await self.bot.db.set_channel(new_channel)
        await interaction.response.send_message(f"Daily message channel {'set' if new else 'updated'} to {new_channel.mention}")

    @app_commands.command(name="daily_channel")
    async def daily_channel(self, interaction: discord.Interaction):
        """Returns the current channel set to receive the daily stock message"""
        channel = await self.bot.db.current_channel(interaction.guild)
        if channel is not None:
            await interaction.response.send_message(f"Currently set to {channel.mention}.\nUse the `?set_daily_channel` command to "
                           f"change this.")
        else:
            await interaction.response.send_message("No channel currently set. Use the `?set_daily_channel` command to change this.")

    @app_commands.command(name="daily_tag")
    async def daily_tag(self, interaction: discord.Interaction, role: discord.Role = None):
        """Used to set a role to be tagged when the daily message is sent"""
        if not role:
            tag = await self.bot.db.get_tag(interaction.guild)
            if tag:
                tag = interaction.guild.get_role(tag)
                await interaction.response.send_message(f"The {tag.name} role is currently set as your daily tag role")
            else:
                await interaction.response.send_message(f"Your server doesn't currently have a daily tag role. Set one with `?daily_tag @role`.")
            return
        try:
            await self.bot.db.add_role_tag(interaction.guild, role)
        except Exception as e:
            await interaction.response.send_message(f"Couldn't set daily tag role: {e}")
            return
        await interaction.response.send_message(f"Successfully updated daily role tag to `{role.name}` for {interaction.guild.name}")
