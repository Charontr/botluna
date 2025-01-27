import discord
from discord.ext import commands
import asyncio
import sqlite3
import os

def is_admin_or_mod(ctx):
    return ctx.author.id == ctx.guild.owner_id or any(role.name == "MOD" for role in ctx.author.roles)

class TicketModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_system_active = {}
        self.ticket_channel_id = {}
        self.ticket_close_timers = {}
        self.mod_role_name = "MOD"
        self.ticket_role_name = "Ticket"
        self.db_path = os.path.join(os.getcwd(), "ticket_database.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()  # setup_database fonksiyonunu çağır
        self.load_ticket_system_status()  # load_ticket_system_status fonksiyonunu çağır

    def setup_database(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sunucular (
                sunucu_id INTEGER PRIMARY KEY,
                ticket_kanal_id INTEGER,
                ticket_sistemi_acik INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def load_ticket_system_status(self):
        # Sunucu bazında ticket sistemi durumunu yükle
        for guild in self.bot.guilds:
            self.cursor.execute("""
                SELECT ticket_kanal_id, ticket_sistemi_acik FROM sunucular WHERE sunucu_id = ?
            """, (guild.id,))
            result = self.cursor.fetchone()
            if result:
                self.ticket_channel_id[guild.id] = result[0]
                self.ticket_system_active[guild.id] = result[1]

    async def on_disconnect(self):
        # Bot ayrıldığında veritabanındaki değişiklikleri kaydet
        self.conn.commit()

    @commands.command(name="ticketsistemaç")
    @commands.check(is_admin_or_mod)
    async def activate_ticket_system(self, ctx):
        # Sunucu bazında ticket sistemi durumunu aç
        self.cursor.execute("""
            INSERT OR IGNORE INTO sunucular (sunucu_id, ticket_kanal_id) VALUES (?, ?)
        """, (ctx.guild.id, None))
        self.conn.commit()
        self.load_ticket_system_status()  # Doğru yere taşıdık
        await ctx.send("Ticket sistemi açıldı.")

    @commands.command(name="ticketsistemkapat")
    @commands.check(is_admin_or_mod)
    async def deactivate_ticket_system(self, ctx):
        # Sunucu bazında ticket sistemi durumunu kapat
        self.cursor.execute("""
            DELETE FROM sunucular WHERE sunucu_id = ?
        """, (ctx.guild.id,))
        self.conn.commit()
        await ctx.send("Ticket sistemi kapatıldı.")

    @commands.command(name="ticket")
    async def create_ticket(self, ctx):
        self.cursor.execute("""
            SELECT ticket_kanal_id, ticket_sistemi_acik FROM sunucular WHERE sunucu_id = ?
        """, (ctx.guild.id,))
        result = self.cursor.fetchone()

        if not result or result[0] is None:
            return await ctx.send("Ticket sistemi şu anda kapalı. !ticketsistemaç komutu ile açabilirsiniz.")

        ticket_channel_id, _ = result
        
        if ctx.channel.id != ticket_channel_id:
            return await ctx.send(f"Bu komutu sadece belirlenen kanalda kullanabilirsiniz. Ticket kanalı: <#{ticket_channel_id}>")

        # Kullanıcının mevcut ticket kontrolü
        user_tickets = [c for c in ctx.guild.channels if c.name.startswith("ticket-") and ctx.author in c.members]
        if user_tickets:
            return await ctx.send("Mevcut bir ticketiniz bulunmaktadır. Lütfen mevcut ticketınız kapatılmadan yeni bir ticket oluşturmaya çalışmayınız.")

        # Ticket oluşturma işlemi
        category_name = "TICKET"
        category = discord.utils.get(ctx.guild.categories, name=category_name)

        if not category:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True)  # Kullanıcıya izin ver
            }

            category = await ctx.guild.create_category(category_name, overwrites=overwrites)

        ticket_channel = await category.create_text_channel(f"ticket-{ctx.author.display_name}")
        self.ticket_close_timers[ticket_channel.id] = self.bot.loop.create_task(self.ticket_close_timer(ticket_channel))

        # Kullanıcıya ticket rolü ver
        ticket_role = discord.utils.get(ctx.guild.roles, name=self.ticket_role_name)
        if not ticket_role:
            # Rol yoksa oluştur
            ticket_role = await ctx.guild.create_role(name=self.ticket_role_name)
            for channel in ctx.guild.channels:
                await channel.set_permissions(ticket_role, read_messages=True, send_messages=True)

        await ctx.author.add_roles(ticket_role)

        welcome_message = f"Merhaba {ctx.author.mention}! Ticket kanalın {ticket_channel.mention} oluşturuldu. Sorularını ve konularını burada paylaşabilirsin."
        await ticket_channel.send(welcome_message)
        await self.notify_mods(ctx.author, ticket_channel)
        await ctx.send(f"Ticket kanalın {ticket_channel.mention} oluşturuldu.")

    @commands.command(name="ticketkapat")
    @commands.check(is_admin_or_mod)
    async def close_ticket_command(self, ctx):
        # Komutun kullanıldığı kanalın bir ticket kanalı olup olmadığını kontrol et
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.send("Bu komut sadece ticket kanallarında kullanılabilir.")

        # Ticket kapatma işlemini gerçekleştir
        await ctx.channel.send("Ticket kapatılıyor...")

        # Kullanıcının ticket rolünü geri al
        ticket_role = discord.utils.get(ctx.guild.roles, name=self.ticket_role_name)
        if ticket_role:
            await ctx.author.remove_roles(ticket_role)

        await self.close_ticket_channel(ctx.channel)

    @commands.command(name="ticketkanalid")
    @commands.check(is_admin_or_mod)
    async def set_ticket_channel(self, ctx, kanal_id: int):
        # Sunucu bazında ticket kanalını ayarla
        self.cursor.execute("""
            INSERT OR REPLACE INTO sunucular (sunucu_id, ticket_kanal_id, ticket_sistemi_acik) VALUES (?, ?, 1)
        """, (ctx.guild.id, kanal_id))
        self.conn.commit()

        # Veritabanına kayıt işlemi
        await ctx.send(f"Ticket kanalı başarıyla ayarlandı: <#{kanal_id}>")
        self.ticket_channel_id[ctx.guild.id] = kanal_id  # ticket_channel_id'yi güncelle
        self.ticket_system_active[ctx.guild.id] = 1  # ticket_system_active'yi True yap

    async def ticket_close_timer(self, channel):
        try:
            await asyncio.sleep(7200)  # 7200 saniye = 2 saat
            await self.close_ticket_channel(channel)
        except asyncio.CancelledError:
            pass

    async def close_ticket_channel(self, channel):
        try:
            await channel.purge(limit=100)
            await channel.delete()

            if channel.id in self.ticket_close_timers:
                self.ticket_close_timers[channel.id].cancel()
                del self.ticket_close_timers[channel.id]

            print(f"Ticket kanalı {channel.name} kapatıldı.")
        except Exception as e:
            print(f"Hata oluştu: {e}")

    async def notify_mods(self, user, ticket_channel):
        mod_role = discord.utils.get(user.guild.roles, name=self.mod_role_name)
        if mod_role:
            mod_users = [member for member in user.guild.members if mod_role in member.roles]
            for mod_user in mod_users:
                try:
                    message = f"{user.mention} tarafından {ticket_channel.mention} adlı bir ticket oluşturuldu. İlgilenmeniz gerekebilir."
                    await mod_user.send(message)
                except Exception as e:
                    print(f"Hata oluştu: {e}")

async def setup(bot):
    await bot.add_cog(TicketModulu(bot))
