import discord
from discord.ext import commands

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} está conectado")

    @commands.command()
    async def ping(self, ctx):
        ping_embed = discord.Embed(title="Ping", color=discord.Color.blue())
        ping_embed.add_field(name=f"Latencia(ms) de {self.bot.user.name}:", value=f"{round(self.bot.latency * 1000)}ms.", inline=False)
        ping_embed.set_footer(text=f"Solicitado por {ctx.author.name}.", icon_url=ctx.author.avatar)
        await ctx.send(embed=ping_embed)

# Asegúrate de que esta función se llama correctamente en tu bot
async def setup(bot):
    await bot.add_cog(Mod(bot))
