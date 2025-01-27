# anket_modulu.py
import discord
from discord.ext import commands
import asyncio
import datetime

def is_admin_or_mod(ctx):
    return ctx.author.id == ctx.guild.owner_id or any(role.name == "MOD" for role in ctx.author.roles)

class AnketModulu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}

    @commands.command(name="anket")
    @commands.check(is_admin_or_mod)
    async def create_poll(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            # Anket başlığını, süresini ve seçenekleri kullanıcıdan al
            await ctx.send("Anket başlığını yazın:")
            title_message = await self.bot.wait_for("message", check=check, timeout=60)
            question = title_message.content

            await ctx.send("Anket süresini dakika cinsinden yazın (örneğin 5):")
            duration_message = await self.bot.wait_for("message", check=check, timeout=60)
            duration = int(duration_message.content)

            await ctx.send("Seçenekleri belirtin (en az iki seçenek girmelisiniz, virgülle ayırın):")
            options_message = await self.bot.wait_for("message", check=check, timeout=60)
            options = [opt.strip() for opt in options_message.content.split(",") if opt.strip()]

            if len(options) < 2:
                raise ValueError("Lütfen en az iki seçenek belirtin.")

            if len(options) > 10:
                raise ValueError("Çok fazla seçenek belirttiniz. En fazla 10 seçenek kullanabilirsiniz.")
        
        except asyncio.TimeoutError:
            await ctx.send("Zaman aşımına uğradı. Anket başlatılamadı.")
            return
        except ValueError as e:
            await ctx.send(f"Hata: {e}")
            return

        end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)
        color = discord.Color.green()  # Renk ekledik

        embed = discord.Embed(
            title="Anket",
            description=question,
            color=color,
            timestamp=end_time
        )

        for i, option in enumerate(options):
            embed.add_field(name=f"Seçenek {i+1}", value=option, inline=False)

        embed.set_footer(text=f"{ctx.author.display_name} tarafından oluşturuldu")

        message = await ctx.send(embed=embed)

        for i in range(1, len(options) + 1):
            await message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")

        self.active_polls[message.id] = {"question": question, "options": options, "votes": [0] * len(options)}

        await asyncio.sleep(duration * 60)
        await self.show_poll_results(ctx, message.id)

    async def show_poll_results(self, ctx, message_id):
        message = await ctx.channel.fetch_message(message_id)
        poll_data = self.active_polls.pop(message_id, None)

        if poll_data:
            total_votes = sum(poll_data["votes"])
            result_message = f"Anket sona erdi!\n\n**{poll_data['question']}**\n\n"

            for i, option in enumerate(poll_data["options"]):
                percentage = (poll_data["votes"][i] / total_votes) * 100 if total_votes > 0 else 0
                result_message += f"{option}: {poll_data['votes'][i]} oy - %{percentage:.2f}\n"

            color = discord.Color.blue()  # Renk ekledik

            embed = discord.Embed(
                title="Anket Sonuçları",
                description=result_message,
                color=color
            )

            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in self.active_polls:
            index = int(payload.emoji.name[0]) - 1
            if 0 <= index < len(self.active_polls[payload.message_id]["votes"]):
                self.active_polls[payload.message_id]["votes"][index] += 1

async def setup(bot):
    await bot.add_cog(AnketModulu(bot))