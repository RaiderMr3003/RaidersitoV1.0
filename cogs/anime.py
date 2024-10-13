import discord  # Importar discord para crear el embed
import requests  #Importar la biblioteca requests para hacer solicitudes HTTP
from googletrans import Translator  #Importar el traductor de Google para traducciones
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown  #Importar la clase CommandOnCooldown para limitar el uso de comandos


def obtener_recomendacion_anime():
    #URL de la API para obtener una recomendación de anime aleatoria
    url = "https://api.jikan.moe/v4/random/anime"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        datos = response.json()  #Convertir la respuesta a formato JSON

        #Obtener la información del anime
        if 'data' in datos:
            anime = datos['data']
            titulo = anime['title']
            url_anime = anime['url']
            sinopsis = anime['synopsis']
            imagen = anime['images']['jpg']['image_url']  #Imagen del anime

            #Inicializar el traductor
            translator = Translator()
            sinopsis_traducida = translator.translate(sinopsis, src='en', dest='es').text

            #Devolver los detalles del anime
            return titulo, sinopsis_traducida, url_anime, imagen
        else:
            return None
    else:
        return None
        
class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} está conectado")


    #Comando para obtener una recomendación de anime aleatoria con un cooldown de 10 segundos
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)  #1 uso cada 10 segundos por usuario
    async def ranime(self, ctx):
        try:
            #Obtener la recomendación de anime
            resultado = obtener_recomendacion_anime()

            if resultado:
                titulo, sinopsis_traducida, url_anime, imagen = resultado

                #Crear el embed
                embed = discord.Embed(
                    title=f"Recomendación de Anime: {titulo}",
                    description=sinopsis_traducida,
                    color=discord.Color.blue()  #Puedes cambiar el color del embed
                )
                embed.set_image(url=imagen)  #Añadir imagen al embed
                embed.add_field(name="Más detalles", value=f"[Ver más]({url_anime})", inline=False)

                #Enviar el embed en el canal
                await ctx.send(embed=embed)
            else:
                await ctx.send("No pude obtener una recomendación en este momento.")
        except CommandOnCooldown as e:
            await ctx.send(f"Espera {e.retry_after:.2f} segundos antes de usar este comando de nuevo.")

#Asegúrate de que esta función se llama correctamente en tu bot
async def setup(bot):
    await bot.add_cog(Anime(bot))
