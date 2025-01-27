import discord
from discord.ext import commands
import random
import json
import asyncio
import sqlite3
import requests

class Oyunlar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dosya_yolu = "trkelimeler.txt"
        self.kazanilan_lunaria = {}
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

    async def kaydet_kazanilan_lunaria(self, ctx, kazanilan_miktar):
        try:
            with sqlite3.connect("bot_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO economy_balances (server_id, user_id, balance)
                    VALUES (?, ?, ?)
                ''', (ctx.guild.id, ctx.author.id, 0))

                cursor.execute('''
                    UPDATE economy_balances
                    SET balance = balance + ?
                    WHERE server_id = ? AND user_id = ?
                ''', (kazanilan_miktar, ctx.guild.id, ctx.author.id))

                connection.commit()

                # Kazanılan lunaria miktarını oyun kanalına mesaj olarak gönder
                await ctx.send(f"{ctx.author.mention}, tebrikler! {kazanilan_miktar} lunaria kazandınız.")
        except Exception as e:
            print(f"Error saving earned lunaria: {e}")

    def yukle_kazanilan_lunaria(self):
        try:
            with sqlite3.connect("bot_database.db") as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    SELECT user_id, balance FROM economy_balances
                    WHERE server_id = ?
                ''', (self.bot.guilds[0].id,))

                results = cursor.fetchall()
                self.kazanilan_lunaria = dict(results)
        except Exception as e:
            print(f"Error loading earned lunaria: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Oyunlar modülü hazır!")
        self.yukle_kazanilan_lunaria()

    @commands.command(name="zar")
    async def zar_at(self, ctx):
        zar_sayisi = random.randint(1, 6)
        await ctx.send(f"{ctx.author.mention}, zar attın ve {zar_sayisi} geldi!")
        self.kazanilan_lunaria[ctx.author.id] = self.kazanilan_lunaria.get(ctx.author.id, 0) + zar_sayisi
        await self.kaydet_kazanilan_lunaria(ctx, zar_sayisi)  # ctx ve kazanılan miktarı ekledik

    @commands.command(name="sayıtahmin")
    async def sayi_tahmin(self, ctx):
        sayi = random.randint(1, 100)
        await ctx.send("1 ile 100 arasında bir sayı tuttum. Tahmin et!")

        def check(m):
            return m.channel == ctx.channel

        while True:
            try:
                tahmin = await self.bot.wait_for("message", check=check, timeout=30)
                tahmin = int(tahmin.content)

                if tahmin < sayi:
                    await ctx.send("Daha yüksek bir sayı dene!")
                elif tahmin > sayi:
                    await ctx.send("Daha düşük bir sayı dene!")
                else:
                    await ctx.send(f"Tebrikler, doğru tahmin! Sayı {sayi} idi.")
                    self.kazanilan_lunaria[ctx.author.id] = self.kazanilan_lunaria.get(ctx.author.id, 0) + 50
                    await self.kaydet_kazanilan_lunaria(ctx, 50)
                    break
            except ValueError as ve:
                await ctx.send(f"Hata: {ve}")
                await ctx.send("Geçerli bir sayı girin!")
            except asyncio.TimeoutError:
                await ctx.send("Zaman aşımına uğradınız. Oyun sona erdi.")
                break

    @commands.command(name="adamasmaca")
    async def adam_asmaca(self, ctx):
        kelimeler = ["elma", "armut", "çilek", "muz", "portakal"]
        kelime = random.choice(kelimeler)
        tahmin_edilen = ["_" for _ in kelime]
        tahmin_hakki = 6

        await ctx.send("Adam asmaca oyununa hoş geldiniz! Kelimeyi tahmin etmek için harf yazın.")

        def check(m):
            return m.channel == ctx.channel

        while True:
            await ctx.send(f"Tahmin hakkınız: {tahmin_hakki}\nTahmin edilen kelime: {' '.join(tahmin_edilen)}")
            try:
                tahmin = await self.bot.wait_for("message", check=check, timeout=30)
                tahmin = tahmin.content.lower()

                if tahmin == kelime:
                    await ctx.send(f"Tebrikler, kelimeyi doğru tahmin ettiniz! Kelime: {kelime}")
                    self.kazanilan_lunaria[ctx.author.id] = self.kazanilan_lunaria.get(ctx.author.id, 0) + 100
                    await self.kaydet_kazanilan_lunaria(ctx, 100)  # ctx ve kazanılan miktarı ekledik
                    break
                elif tahmin in kelime:
                    for i in range(len(kelime)):
                        if kelime[i] == tahmin:
                            tahmin_edilen[i] = tahmin
                    if "_" not in tahmin_edilen:
                        await ctx.send(f"Tebrikler, kelimeyi doğru tahmin ettiniz! Kelime: {kelime}")
                        self.kazanilan_lunaria[ctx.author.id] = self.kazanilan_lunaria.get(ctx.author.id, 0) + 100
                        await self.kaydet_kazanilan_lunaria(ctx, 100)  # ctx ve kazanılan miktarı ekledik
                        break
                else:
                    tahmin_hakki -= 1
                    if tahmin_hakki == 0:
                        await ctx.send(f"Maalesef, tahmin hakkınız bitti. Doğru kelime: {kelime}")
                        break
                    await ctx.send(f"Yanlış tahmin! Kalan tahmin hakkınız: {tahmin_hakki}")
            except asyncio.TimeoutError:
                await ctx.send("Zaman aşımına uğradınız. Oyun sona erdi.")
                break

async def setup(bot):
    await bot.add_cog(Oyunlar(bot))