# antikufur_modulu.py
import discord
from discord.ext import commands
import os
import json

class AntiKufurModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kufur_listesi = self.load_kufur_listesi()
        self.sunucu_ayarları = self.load_sunucu_ayarları()

    def load_kufur_listesi(self):
        try:
            with open('kufur.txt', 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print("kufur.txt not found. Creating an empty file.")
            with open('kufur.txt', 'w', encoding='utf-8'):
                pass
            return []

    def load_sunucu_ayarları(self):
        try:
            with open('sunucu_ayarları.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("sunucu_ayarları.json not found. Creating an empty file.")
            with open('sunucu_ayarları.json', 'w') as file:
                json.dump({}, file)
            return {}

    def save_sunucu_ayarları(self):
        with open('sunucu_ayarları.json', 'w') as file:
            json.dump(self.sunucu_ayarları, file, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.antikufur_aktif(message.guild.id):
            return

        content = message.content.lower()
        for kufur in self.kufur_listesi:
            if kufur in content:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, lütfen küfürlü dil kullanma!")
                break

    def antikufur_aktif(self, sunucu_id):
        return self.sunucu_ayarları.get(str(sunucu_id), True)

    @commands.command(name='antiküfüraç')
    async def antikufur_ac(self, ctx):
        if self.is_mod_or_owner(ctx.author):
            self.sunucu_ayarları[str(ctx.guild.id)] = True
            self.save_sunucu_ayarları()
            await ctx.send("Antiküfür sistemi açıldı.")
        else:
            await ctx.send("Bu komutu sadece sunucu sahibi ve MOD rolüne sahip kişiler kullanabilir.")

    @commands.command(name='antiküfürkapat')
    async def antikufur_kapat(self, ctx):
        if self.is_mod_or_owner(ctx.author):
            self.sunucu_ayarları[str(ctx.guild.id)] = False
            self.save_sunucu_ayarları()
            await ctx.send("Antiküfür sistemi kapatıldı.")
        else:
            await ctx.send("Bu komutu sadece sunucu sahibi ve MOD rolüne sahip kişiler kullanabilir.")

    @commands.command(name='antiküfür', aliases=['küfürsistemi'])
    async def antikufur_kontrol(self, ctx):
        if self.is_mod_or_owner(ctx.author):
            await ctx.send("Antiküfür sistemi açık.")
        else:
            await ctx.send("Bu komutu kullanabilmek için gerekli yetkiye sahip değilsiniz.")

    def is_mod_or_owner(self, member):
        return member.guild.owner_id == member.id or any(role.name == "MOD" for role in member.roles)

async def setup(bot):
    await bot.add_cog(AntiKufurModulu(bot))
