import discord
from discord.ext import commands
import os
from discord.ext.commands import has_permissions, CheckFailure
from modules.settings import get_update_channel, set_update_channel, execute_sql_query

def is_admin_or_mod(ctx):
    return ctx.author.id == ctx.guild.owner_id or any(role.name == "MOD" for role in ctx.author.roles)

class UpdateModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "update.txt"
        self.channel_name = "luna-update"

class UpdateModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "update.txt"
        self.channel_name = "luna-update"

    async def create_channel_if_not_exists(self, guild):
        channel_id = get_update_channel(guild.id)

        if not channel_id:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await guild.create_text_channel(self.channel_name, overwrites=overwrites)
            set_update_channel(guild.id, channel.id)
        else:
            channel = guild.get_channel(channel_id)

        return channel

    async def send_update_message(self, guild):
        channel_id = get_update_channel(guild.id)

        if channel_id:
            channel = guild.get_channel(channel_id)

            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                await channel.send(content)
                await channel.send("Güncelleme mesajı gönderildi.")

    @commands.command(name="update")
    @commands.check(is_admin_or_mod)
    async def update_message(self, ctx):
        await self.send_update_message(ctx.guild)
        await ctx.send("Güncelleme mesajı gönderildi.")

    @commands.command(name="updateid")
    @commands.check(is_admin_or_mod)
    async def set_update_channel_command(self, ctx):
        channel_id = ctx.message.channel.id
        set_update_channel(ctx.guild.id, channel_id)
        await ctx.send(f"Güncelleme mesajlarının gönderileceği kanal ayarlandı: <#{channel_id}>.")

async def setup(bot):
    await bot.add_cog(UpdateModulu(bot))
