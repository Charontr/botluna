# roleklesil.py
from discord.ext import commands

def is_admin_or_mod(ctx):
    return ctx.author.id == ctx.guild.owner_id or any(role.name == "MOD" for role in ctx.author.roles)

class Rolmodulu1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rolekle")
    @commands.check(is_admin_or_mod)
    async def add_role(self, ctx, role_id):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)
            if role:
                for member in ctx.guild.members:
                    await member.add_roles(role)
                await ctx.send(f"{role.name} rolü sunucudaki tüm üyelere eklendi.")
            else:
                await ctx.send("Belirtilen rol bulunamadı.")
        except ValueError:
            await ctx.send("Geçersiz rol ID'si.")

    @commands.command(name="rolsil")
    @commands.check(is_admin_or_mod)
    async def remove_role(self, ctx, role_id):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)
            if role:
                for member in ctx.guild.members:
                    await member.remove_roles(role)
                await ctx.send(f"{role.name} rolü sunucudaki tüm üyelerden kaldırıldı.")
            else:
                await ctx.send("Belirtilen rol bulunamadı.")
        except ValueError:
            await ctx.send("Geçersiz rol ID'si.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Bu komutu kullanma izniniz yok.")
        else:
            # Diğer hata türlerini burada ele alabilirsiniz
            print(f"Hata: {error}")
            

async def setup(bot):
    await bot.add_cog(Rolmodulu1(bot))
