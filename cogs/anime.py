import discord
from discord.ext import commands
from googletrans import Translator
import requests


def obtener_recomendacion_anime():
    url = "https://api.jikan.moe/v4/random/anime"
    response = requests.get(url)
    if response.status_code == 200:
        datos = response.json()

        # Verificar la estructura de los datos
        if 'data' in datos:
            anime = datos['data']  # Ahora es un diccionario, no una lista
            titulo = anime['title']
            url_anime = anime['url']
            sinopsis = anime['synopsis']

            # Inicializar el traductor aquí
            translator = Translator()
            # Traducir la sinopsis al español
            sinopsis_traducida = translator.translate(sinopsis, src='en', dest='es').text

            return f"La recomendación random es: **{titulo}**\n{sinopsis_traducida}\nMás detalles: {url_anime}"
        else:
            return "No se encontraron datos de anime disponibles."
    else:
        return "No pude obtener una recomendación en este momento."
        
class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} está conectado")

    @commands.command()
    async def ranime(self, ctx):
        recomendacion = obtener_recomendacion_anime()
        await ctx.send(recomendacion)

# Asegúrate de que esta función se llama correctamente en tu bot
async def setup(bot):
    await bot.add_cog(Anime(bot))
