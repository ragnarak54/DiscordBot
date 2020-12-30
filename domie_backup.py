import discord
from discord.ext import commands
import asyncio
import datetime


class DomieV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.domieMember = self.bot.get_guild(208387395614277633).get_member(405489655165747200)
        print(self.domieMember)

    def domie_check(self, message):
        return message.author == self.domieMember

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == '!wb':
            try:
                await self.bot.wait_for('message', check=self.domie_check, timeout=1)
                print('replied')
            except asyncio.TimeoutError:
                await message.channel.send("offline")
                now = datetime.datetime.now()
                dayOfWeek = (now.getUTCDay() + 6) % 7;
                var
                hourOfWeek = now.getUTCHours() + (24 * dayOfWeek);
                var
                hTill = (6 - (hourOfWeek % 7) + 2) % 7;
                var
                mTill = 60 - now.getUTCMinutes();
                if (mTill === 60) {
                hTill++;
                mTill = 0;
                }
                var
                timestr = '';
                if (hTill > 0) {
                timestr += hTill + ' hour' + (hTill > 1 ? 's': '');
                if (mTill > 0) {
                timestr += ' and ' + mTill + ' minute' + (mTill == = 1 ? '': 's');
                }
                }
                else {
                    timestr += mTill + ' minute' + (mTill === 1 ? '': 's');
                }

