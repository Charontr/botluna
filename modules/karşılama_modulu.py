#karşılama_modulu.py

import discord
from discord.ext import commands
from modules.settings import set_welcome_channel, get_welcome_channel, set_welcome_message, get_welcome_message

def is_admin_or_mod(ctx):
    return ctx.author.id == ctx.guild.owner_id or any(role.name == "MOD" for role in ctx.author.roles)

class KarsilamaModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="karşılamakanalid")
    @commands.check(is_admin_or_mod)
    async def karşılama_id(self, ctx, kanal_id):
        guild_id = ctx.guild.id

        try:
            kanal_id = int(kanal_id)
            set_welcome_channel(guild_id, kanal_id)
            await ctx.send(f"Karşılama kanalı ayarlandı: {kanal_id}")
        except ValueError:
            await ctx.send("Geçersiz kanal ID'si. Lütfen geçerli bir sayı girin.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        kanal_id = get_welcome_channel(guild_id)
        karşılama_mesaj = get_welcome_message(guild_id)

        if kanal_id:
            kanal = member.guild.get_channel(kanal_id)

            if kanal:
                try:
                    if karşılama_mesaj:
                        karşılama_mesaj = karşılama_mesaj.replace("{user}", member.mention)
                        await kanal.send(karşılama_mesaj)
                    else:
                        await kanal.send(f"{member.mention} sunucuya hoş geldin! Burada keyifli vakit geçirmen dileğiyle.")
                except discord.errors.Forbidden:
                    pass
            else:
                await member.guild.system_channel.send("Karşılama kanalı bulunamadı. Lütfen bir kanal ayarlayın.")
        else:
            await member.guild.system_channel.send("Karşılama kanalı ayarlanmamış. Lütfen bir kanal ayarlayın.")

async def setup(bot):
    await bot.add_cog(KarsilamaModulu(bot))