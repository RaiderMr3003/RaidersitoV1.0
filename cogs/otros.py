import discord
import requests
from discord.ext import commands

class Otros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} está conectado")

    #Comando para obtener una imagen random de pug (son graciosos)
    @commands.command()
    async def pug(self, ctx):
        #Hacer una solicitud a la API para obtener una imagen random de pug
        response = requests.get("https://dog.ceo/api/breed/pug/images/random")
        data = response.json()
        image_url = data["message"]
    
        #Enviar la imagen al canal de Discord
        await ctx.send(image_url)

#Asegúrate de que esta función se llama correctamente en tu bot
async def setup(bot):
    await bot.add_cog(Otros(bot))
