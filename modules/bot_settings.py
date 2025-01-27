import discord
from discord.ext import commands
import sqlite3
import logging
import asyncio
from discord.ui import View, Select, Button

class BotSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS settings (
                        guild_id INTEGER NOT NULL,
                        setting_name TEXT NOT NULL,
                        setting_value TEXT,
                        PRIMARY KEY (guild_id, setting_name)
                    )
                    """
                )
                conn.commit()
            logging.info("Veritabanı başlatıldı.")
        except Exception as e:
            logging.critical(f"Veritabanı başlatılırken bir hata oluştu: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Bot ayarları modülü yüklendi!")

    @commands.command(name="ayarlar", description="Sunucu ayarlarını düzenlemek için menüyü açar.")
    async def ayarlar(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🛠️ Sunucu Ayarları",
            description="Aşağıdaki butonlara tıklayarak sunucu ayarlarını düzenleyebilirsiniz.",
            color=discord.Color.blue(),
        )
        view = BotSettingsView(self.bot)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="get_ayar", description="Belirli bir ayarı görüntüler.")
    async def get_ayar(self, ctx: commands.Context, setting_name: str):
        try:
            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT setting_value FROM settings WHERE guild_id = ? AND setting_name = ?",
                    (ctx.guild.id, setting_name),
                )
                result = cursor.fetchone()

            if result:
                await ctx.send(f"`{setting_name}` ayarı: {result[0]}")
            else:
                await ctx.send(f"`{setting_name}` ayarı bulunamadı.")
                logging.info(f"Ayar bulunamadı: {ctx.guild.id}, {setting_name}")
        except Exception as e:
            logging.error(f"Ayar getirilirken bir hata oluştu: {e}")
            await ctx.send("Bir hata oluştu.")

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

    def set_setting(self, guild_id, setting_name, setting_value):
        try:
            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (guild_id, setting_name, setting_value) VALUES (?, ?, ?)",
                    (guild_id, setting_name, setting_value),
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Ayar ayarlanırken bir hata oluştu: {e}")

class BotSettingsView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Otorol Ayarları", style=discord.ButtonStyle.primary, custom_id="otorol")
    async def otorol_settings(self, interaction: discord.Interaction, button: Button):
        roles = [discord.SelectOption(label=role.name, value=str(role.id)) for role in interaction.guild.roles if role.name != "@everyone"]
        roles = roles[:25]

        select = Select(placeholder="Bir rol seçin", options=roles)

        async def select_callback(interaction: discord.Interaction):
            role_id = int(select.values[0])
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            self.set_setting(interaction.guild.id, "otorol", role.id)
            await interaction.response.send_message(f"{role.name} rolü otorol olarak ayarlandı.", ephemeral=True)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Bir rol seçin:", view=view, ephemeral=True)

    async def set_setting(self, guild_id, setting_name, setting_value):
        try:
            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (guild_id, setting_name, setting_value) VALUES (?, ?, ?)",
                    (guild_id, setting_name, setting_value),
                )
                conn.commit()
                logging.info(f"Ayar ayarlandı: {guild_id}, {setting_name}, {setting_value}")
        except Exception as e:
            logging.error(f"Ayar ayarlanırken bir hata oluştu: {e}")

    @discord.ui.button(label="Küfür Filtresi", style=discord.ButtonStyle.danger, custom_id="kufur")
    async def kufur_settings(self, interaction: discord.Interaction, button: Button):
        try:
            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT setting_value FROM settings WHERE guild_id = ? AND setting_name = ?",
                    (interaction.guild.id, "kufur_filtresi"),
                )
                result = cursor.fetchone()

            current_status = result[0] == "1" if result else False
            new_status = not current_status

            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (guild_id, setting_name, setting_value) VALUES (?, ?, ?)",
                    (interaction.guild.id, "kufur_filtresi", "1" if new_status else "0"),
                )
                conn.commit()

            status_message = "aktif edildi" if new_status else "devre dışı bırakıldı"
            await interaction.response.send_message(f"Küfür filtresi {status_message}.", ephemeral=True)
            logging.info(f"Küfür filtresi ayarlandı: {interaction.guild.id}, {new_status}")
        except Exception as e:
            logging.error(f"Küfür filtresi ayarlanırken bir hata oluştu: {e}")
            await interaction.response.send_message("Bir hata oluştu.", ephemeral=True)

    @discord.ui.button(label="Hoş Geldin Mesajı", style=discord.ButtonStyle.success, custom_id="hosgeldin")
    async def hosgeldin_settings(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Yeni üyeler için hoş geldin mesajını ayarlamak için mesajınızı girin (mesajı doğrudan cevap olarak yazabilirsiniz):",
            ephemeral=True
        )

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            message = await self.bot.wait_for("message", check=check, timeout=60)
            self.set_setting(interaction.guild.id, "hosgeldin_mesaji", message.content)
            await interaction.followup.send(f"Hoş geldin mesajı ayarlandı: {message.content}")
            logging.info(f"Hoş geldin mesajı ayarlandı: {interaction.guild.id}, {message.content}")
        except asyncio.TimeoutError:
            await interaction.followup.send("Hoş geldin mesajı ayarlanmadı. Zaman aşımına uğradı.")
            logging.warning(f"Hoş geldin mesajı zaman aşımına uğradı: {interaction.guild.id}")
        except Exception as e:
            logging.error(f"Hoş geldin mesajı ayarlanırken bir hata oluştu: {e}")
            await interaction.followup.send("Bir hata oluştu.")

    @discord.ui.button(label="Prefix Ayarları", style=discord.ButtonStyle.primary, custom_id="prefix")
    async def prefix_settings(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "Yeni komut prefixini belirlemek için bir prefix girin (mesajı doğrudan cevap olarak yazabilirsiniz):",
            ephemeral=True
        )

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            message = await self.bot.wait_for("message", check=check, timeout=60)
            self.set_setting(interaction.guild.id, "prefix", message.content)
            await interaction.followup.send(f"Prefix ayarlandı: {message.content}")
            logging.info(f"Prefix ayarlandı: {interaction.guild.id}, {message.content}")
        except asyncio.TimeoutError:
            await interaction.followup.send("Prefix ayarlanmadı. Zaman aşımına uğradı.")
            logging.warning(f"Prefix ayarı zaman aşımına uğradı: {interaction.guild.id}")
        except Exception as e:
            logging.error(f"Prefix ayarlanırken bir hata oluştu: {e}")
            await interaction.followup.send("Bir hata oluştu.")

    @discord.ui.button(label="Modül Yönetimi", style=discord.ButtonStyle.secondary, custom_id="modul")
    async def module_settings(self, interaction: discord.Interaction, button: Button):
        modules = ["Ekonomi", "Oyunlar", "Küfür Filtresi", "Hoş Geldin Mesajı"]
        options = [discord.SelectOption(label=mod, value=mod.lower()) for mod in modules]

        select = Select(placeholder="Bir modül seçin", options=options)

        async def select_callback(interaction: discord.Interaction):
            module_name = select.values[0]
            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT setting_value FROM settings WHERE guild_id = ? AND setting_name = ?",
                    (interaction.guild.id, f"modul_{module_name}"),
                )
                result = cursor.fetchone()

            current_status = result[0] == "1" if result else False
            new_status = not current_status

            with sqlite3.connect("bot_database.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (guild_id, setting_name, setting_value) VALUES (?, ?, ?)",
                    (interaction.guild.id, f"modul_{module_name}", "1" if new_status else "0"),
                )
                conn.commit()

            status_message = "aktif edildi" if new_status else "devre dışı bırakıldı"
            await interaction.response.send_message(f"{module_name} modülü {status_message}.", ephemeral=True)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Bir modül seçin:", view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(BotSettings(bot))
