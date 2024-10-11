import requests  #Importar la biblioteca requests para hacer solicitudes HTTP
from googletrans import Translator  #Importar el traductor de Google para traducciones
from discord.ext import commands

def obtener_recomendacion_anime():
    #URL de la API para obtener una recomendación de anime aleatoria
    url = "https://api.jikan.moe/v4/random/anime"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        datos = response.json()  #Convertir la respuesta a formato JSON

        # Obtener la información del anime
        if 'data' in datos:
            anime = datos['data']  
            titulo = anime['title']  
            url_anime = anime['url']  
            sinopsis = anime['synopsis'] 

            # Inicializar el traductor
            translator = Translator()
            sinopsis_traducida = translator.translate(sinopsis, src='en', dest='es').text

            # Devolver la recomendación formateada
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


    #Comando para obtener una recomendación de anime aleatoria
    @commands.command()
    async def ranime(self, ctx):
       
        recomendacion = obtener_recomendacion_anime()
        await ctx.send(recomendacion)

async def setup(bot):
    await bot.add_cog(Anime(bot))
