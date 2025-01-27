import discord
from discord.ext import commands
import sqlite3

def is_admin_or_mod(ctx):
    return ctx.author.id == ctx.guild.owner_id or any(role.name == "MOD" for role in ctx.author.roles)

class Ekonomi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()

    def initialize_database(self):
        try:
            with sqlite3.connect("bot_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS economy_balances (
                        server_id INTEGER,
                        user_id INTEGER,
                        balance INTEGER,
                        PRIMARY KEY (server_id, user_id)
                    )
                ''')
                connection.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")

    def on_ready(self):
        print("Ekonomi modülü hazır!")

    @commands.command(name="bakiye", description="Mevcut bakiyenizi kontrol edin.")
    async def bakiye(self, ctx, user: discord.Member = None):
        user = user or ctx.author

        try:
            with sqlite3.connect("bot_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO economy_balances (server_id, user_id, balance)
                    VALUES (?, ?, ?)
                ''', (ctx.guild.id, user.id, 50))

                cursor.execute('''
                    SELECT balance FROM economy_balances
                    WHERE server_id = ? AND user_id = ?
                ''', (ctx.guild.id, user.id))

                result = cursor.fetchone()
                balance = result[0] if (result and result[0]) else 0

                await ctx.send(f"{user.mention}, mevcut bakiyeniz: {balance} lunaria")
        except Exception as e:
            await ctx.send(f"Hata oluştu: {e}")

    @commands.command(name="paraekle", description="Belirli bir kullanıcının hesabına para ekleyin.", usage="<kullanıcı> <miktar>")
    @commands.check(is_admin_or_mod)
    async def para_ekle(self, ctx, user: discord.Member, miktar: int):
        try:
            if miktar <= 0:
                await ctx.send("Geçersiz miktar. Pozitif bir miktar giriniz.")
                return

            with sqlite3.connect("bot_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO economy_balances (server_id, user_id, balance)
                    VALUES (?, ?, ?)
                ''', (ctx.guild.id, user.id, 0))

                cursor.execute('''
                    UPDATE economy_balances
                    SET balance = balance + ?
                    WHERE server_id = ? AND user_id = ?
                ''', (miktar, ctx.guild.id, user.id))

                cursor.execute('''
                    SELECT balance FROM economy_balances
                    WHERE server_id = ? AND user_id = ?
                ''', (ctx.guild.id, user.id))

                result = cursor.fetchone()
                yeni_bakiye = result[0] if (result and result[0]) else 0

                await ctx.send(f"{user.mention}, hesabına {miktar} lunaria eklendi. Yeni bakiye: {yeni_bakiye}")
        except Exception as e:
            await ctx.send(f"Hata oluştu: {e}")

    @commands.command(name="parasil", description="Belirli bir kullanıcının hesabından para silin.", usage="<kullanıcı> <miktar>")
    @commands.check(is_admin_or_mod)
    async def para_sil(self, ctx, user: discord.Member, miktar: int):
        try:
            if miktar <= 0:
                await ctx.send("Geçersiz miktar. Pozitif bir miktar giriniz.")
                return

            with sqlite3.connect("bot_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO economy_balances (server_id, user_id, balance)
                    VALUES (?, ?, ?)
                ''', (ctx.guild.id, user.id, 0))

                cursor.execute('''
                    UPDATE economy_balances
                    SET balance = balance - ?
                    WHERE server_id = ? AND user_id = ?
                ''', (miktar, ctx.guild.id, user.id))

                cursor.execute('''
                    SELECT balance FROM economy_balances
                    WHERE server_id = ? AND user_id = ?
                ''', (ctx.guild.id, user.id))

                result = cursor.fetchone()
                yeni_bakiye = result[0] if (result and result[0]) else 0

                await ctx.send(f"{user.mention}, hesabından {miktar} lunaria silindi. Yeni bakiye: {yeni_bakiye}")
        except Exception as e:
            await ctx.send(f"Hata oluştu: {e}")

    # Diğer fonksiyonları buraya ekleyebilirsiniz...

async def setup(bot):
    await bot.add_cog(Ekonomi(bot))