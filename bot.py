import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import importlib
import logging

# .env dosyasını yükle
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if DISCORD_TOKEN is None:
    print("Discord token not found in the .env file. Please add it and restart the bot.")
    exit()

# Loglama ayarları
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Bot ayarları
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Event Handlers
@bot.event
async def on_ready():
    print(f"Bot is ready! {bot.user}")
    bot.remove_command("help")  # Default help komutunu kaldır

    # Dinamik modül yükleme
    modules_folder = os.path.join(os.path.dirname(__file__), 'modules')
    for file in os.listdir(modules_folder):
        if file.endswith('.py') and not file.startswith('__'):
            module_name = f"modules.{file[:-3]}"  # Modül adını oluştur
            try:
                await bot.load_extension(module_name)  # Modülü yükle
                logging.info(f"Loaded module: {module_name}")
            except Exception as e:
                logging.error(f"Failed to load module {module_name}: {e}")

@bot.event
async def on_guild_join(guild):
    owner = guild.owner
    message = (
        f"Merhaba {owner.mention}! Ben Luna. Beni sunucunuza davet ettiğiniz için teşekkür ederim. "
        f"Prefix'im varsayılan olarak `!` şeklinde atandı. Sunucunuzda `!yardım` komutu ile "
        f"değiştirebileceğiniz ayarları görebilirsiniz.\n"
        f"Bazı özellikler: \n"
        f"- Otomatik rol sistemi \n"
        f"- Ekonomi sistemi \n"
        f"- Moderasyon komutları\n"
        f"Daha fazlası için beni kullanmaya başlayın!"
    )
    try:
        await owner.send(message)
    except discord.Forbidden:
        logging.warning(f"Could not send welcome message to {owner}. Permission denied.")

# Bot'u çalıştır
try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    logging.critical(f"Bot failed to start: {e}")
