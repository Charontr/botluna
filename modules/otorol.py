# otorol.py
import discord
from discord.ext import commands
from discord.utils import get
from modules.settings import get_user_role, set_user_role, get_bot_role, set_bot_role
from modules.settings import set_user_role_command, set_bot_role_command

def is_admin_or_mod(ctx):
    return ctx.author.id == ctx.guild.owner_id or any(role.name == "MOD" for role in ctx.author.roles)

class OtomatikRolModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        user_role_id = get_user_role(member.guild.id)
        bot_role_id = get_bot_role(member.guild.id)

        if user_role_id:
            user_role = get(member.guild.roles, id=user_role_id)
            if user_role:
                await member.add_roles(user_role)
                print(f"{member.name} kullanıcısına otomatik kullanıcı rolü atandı: {user_role.name}")

        if bot_role_id and member.bot:
            bot_role = get(member.guild.roles, id=bot_role_id)
            if bot_role:
                await member.add_roles(bot_role)
                print(f"{member.name} kullanıcısına otomatik bot rolü atandı: {bot_role.name}")

    @commands.command(name="kullanıcırolayarla")
    @commands.check(is_admin_or_mod)
    async def set_user_role_command(self, ctx, role_id):
        set_user_role_command(ctx.guild.id, role_id)
        await ctx.send(f"Otomatik kullanıcı rolü komutu başarıyla ayarlandı: {role_id}")

    @commands.command(name="botrolayarla")
    @commands.check(is_admin_or_mod)
    async def set_bot_role_command(self, ctx, role_id):
        set_bot_role_command(ctx.guild.id, role_id)
        await ctx.send(f"Otomatik bot rolü komutu başarıyla ayarlandı: {role_id}")    

async def setup(bot):
    await bot.add_cog(OtomatikRolModulu(bot))