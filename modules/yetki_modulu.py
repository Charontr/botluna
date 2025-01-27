import logging
import discord
from discord.ext import commands
import sqlite3

class YetkiModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_setting(self, guild_id, setting_name):
        try:
            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT setting_value FROM settings WHERE guild_id = ? AND setting_name = ?",
                    (guild_id, setting_name),
                )
                result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Ayar getirilirken bir hata oluştu: {e}")
            return None

    @commands.command(name='yetkiver')
    async def yetkiver(self, ctx, kullanici: discord.Member):
        mod_role_id = self.get_setting(ctx.guild.id, "mod_role")
        mod_role = ctx.guild.get_role(int(mod_role_id)) if mod_role_id else None

        if mod_role and (ctx.author == ctx.guild.owner or mod_role in ctx.author.roles):
            await kullanici.add_roles(mod_role)
            await ctx.send(f"{kullanici.mention} kullanıcısına Moderasyon yetkisi verildi.")
        else:
            await ctx.send("Bu komutu sadece sunucu sahibi ve MOD rolüne sahip kişiler kullanabilir.")

async def setup(bot):
    await bot.add_cog(YetkiModulu(bot))
