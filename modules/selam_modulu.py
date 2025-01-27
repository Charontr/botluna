# selam_modulu.py
import discord
from discord.ext import commands

from modules.settings import get_gif_link, get_prefix, set_gif_link

def is_mod_or_owner():
    async def predicate(ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="MOD")  # Mod rolünün adını değiştirin
        return ctx.author == ctx.guild.owner or (mod_role and mod_role in ctx.author.roles)

    return commands.check(predicate)

def has_mod_permissions():
    async def predicate(ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="MOD")  # Mod rolünün adını değiştirin
        return mod_role and mod_role in ctx.author.roles

    return commands.check(predicate)

class SelamModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.selam_listesi = {
            "sa": "as",
            "selamun aleyküm": "aleyküm selam",
            "merhaba": "Merhaba!",
            "selam": "Selam!",
            "günaydın": "Günaydın! ☀️",
        }

        self.oyun_durumu_tepkileri = {
            discord.ActivityType.playing: "Oyun oynarken keyifli zamanlar geçir",
            discord.ActivityType.listening: "Dinlerken keyif alıyorsun sanırım",
            discord.ActivityType.watching: "İzlerken keyifli bir zaman geçir",
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if not self.check_prefix(message.content):
            if message.content.lower() in ["selam", "merhaba", "günaydın", "sa", "selamun aleyküm"]:
                await self.handle_selam(message)

    async def handle_selam(self, message):
        user = message.author
        selam = message.content.lower()

        durum_tepkisi = self.oyun_durumu_tepkileri.get(type(user.activity), None)
        if durum_tepkisi:
            response = f"{durum_tepkisi}, {user.mention}!"
        else:
            response = f"{self.selam_listesi.get(selam)} {user.mention}!"

        if selam == "günaydın":
            response += " ☀️"
            await message.channel.send(response)
            server_id = message.guild.id
            gif_link = get_gif_link(server_id)
            await message.channel.send(gif_link)
        else:
            await message.channel.send(response)

    @commands.command(name="günaydıngif")
    @is_mod_or_owner()
    async def set_gif_link(self, ctx, gif_link):
        server_id = ctx.guild.id
        set_gif_link(server_id, gif_link)
        await ctx.send(f"Gif linki başarıyla ayarlandı: {gif_link}")

    def check_prefix(self, content):
        prefix = get_prefix(self.bot, None)
        return content.startswith(prefix) if (prefix and isinstance(prefix, str)) else False

async def setup(bot):
    await bot.add_cog(SelamModulu(bot))