import discord
from discord.ext import commands
from modules.settings import get_prefix, set_prefix, get_gif_link, set_gif_link

class YardimModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pages = [
            {
                "title": "Sunucu Ayarları",
                "description": "ADMİN,MODERATÖR ÖZEL",
                "fields": [
                    {"name": "prefixayarla", "value": "sunucu prefix'ini değiştirir"},
                    {"name": "antiküfüraç", "value": "antiküfür sistemini açar"},
                    {"name": "antiküfürkapat", "value": "antiküfür sistemini kapatır"},
                    {"name": "antiküfür", "value": "sistemin açık,kapalı olup olmadığını kontrol eder"},
                    {"name": "anket", "value": "Anket oluşturur"},
                    {"name": "paraekle @kullanıcı (miktar)", "value": "seçilen kişiye belirtilen miktarda para ekler"},
                    {"name": "parasil @kullanıcı (miktar)", "value": "seçilen kişiden belirtilen miktarda para siler"},
                    {"name": "karşılamakanalid (kanalid)", "value": "sunucuya biri girdiği zaman ayarlanan kanala hoşgeldin mesajı gönderir"},
                    {"name": "kullanıcırolayarla (rolid)", "value": "sunucuya kullanıcı katıldığı zaman belirtilen rolü otomatik verir"},
                    {"name": "botrolayarla (rolid)", "value": "sunucuya bot katıldığı zaman belirtilen rolü otomatik verir"},
                    {"name": "rolekle (rolid)", "value": "belirtilen rolü sunucudaki tüm kullanıcılara ekler"},
                    {"name": "rolsil", "value": "belirtilen rolü sunucudaki tüm kullanıcılardan siler"},
                    {"name": "günaydıngif (giflink)", "value": "günaydın mesajında gönderilecek gif'i ayarlar"},
                    {"name": "ticketsistemaç", "value": "ticket sistemini açar"},
                    {"name": "ticketsistemkapat", "value": "ticket sistemini kapatır"},
                    {"name": "ticketkanalid (kanalid)", "value": "!ticket komutunun kullanılacağı kanalı ayarlar"},
                    {"name": "updateid", "value": "bu komutun yazıldığı kanalı update mesajlarının gönderileceği kanal olarak ayarlar"},
                    {"name": "update", "value": "update mesajlarını ayarlanan kanala gönderir"},
                    {"name": "yetkiver @kullanıcı", "value": "Botun sunucu ayarları kısmındaki komutları kullanmabilmesi için kişiye yetki verir"}

                ]
            },
            {
                "title": "Yardımcı Bot Komutları",
                "description": "Kullanıcılar için",
                "fields": [
                    {"name": "prefix", "value": "Botun sunucuda kullandığı prefixi gösterir"},
                    {"name": "bakiye", "value": "Kullanıcının sunucudaki bakiyesini gösterir"},
                    {"name": "ticket", "value": "Sorunlarınız için Destek ekibine ticket gönderilir"},
                    {"name": "yardım", "value": "bot'a ait kullanılabilir komutları gösterir"},
                    
                ]
            },

                        {
                "title": "Eğlence Komutları",
                "description": "Sunucudaki eğlence komutları",
                "fields": [
                    {"name": "Zar", "value": "1-6 arası zar atar"},
                    {"name": "sayıtahmin", "value": "sayıtahmin oyunu oynanır"},
                    {"name": "adamasmaca", "value": "adamasmaca oynanır"},
                    {"name": "savaş", "value": "bot ile full oto savaş yapılır"},
                ]
            },
            # Başka sayfaları buraya ekleyebilirsiniz
        ]
        self.current_page = 0

    @commands.command(name="yardım")
    async def show_help(self, ctx):
        embed = self.create_embed()
        message = await ctx.send(embed=embed)
        await self.add_reactions(message)

    async def add_reactions(self, message):
        if len(self.pages) > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")

    def create_embed(self):
        page = self.pages[self.current_page]
        embed = discord.Embed(
            title=page["title"],
            description=page["description"],
            color=discord.Color.gold()  # Renk değiştirildi
        )

        for field in page["fields"]:
            embed.add_field(name=field["name"], value=field.get("value", ""), inline=False)

        return embed

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        message = reaction.message
        if message.author == self.bot.user and message.embeds:
            emoji = str(reaction.emoji)

            if emoji == "⬅️":
                self.current_page = (self.current_page - 1) % len(self.pages)
            elif emoji == "➡️":
                self.current_page = (self.current_page + 1) % len(self.pages)

            embed = self.create_embed()
            await message.edit(embed=embed)
            await reaction.remove(user)

async def setup(bot):
    await bot.add_cog(YardimModulu(bot))
