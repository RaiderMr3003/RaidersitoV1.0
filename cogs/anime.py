import discord  #Importar discord para crear el embed
import requests  #Importar la biblioteca requests para hacer solicitudes HTTP
from googletrans import Translator  #Importar el traductor de Google para traducciones
from discord.ext import commands


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
            calificacion = anime.get('score', 'N/A')  # Obtener la calificación (score), si no está disponible mostrar "N/A"

            #Inicializar el traductor
            translator = Translator()
            sinopsis_traducida = translator.translate(sinopsis, src='en', dest='es').text

            #Devolver los detalles del anime
            return titulo, sinopsis_traducida, url_anime, imagen, calificacion
        else:
            return None
    else:
        return None

#Función para buscar un anime específico
def buscar_anime(query):
    #URL de la API de Jikan para buscar un anime por título
    url = f"https://api.jikan.moe/v4/anime?q={query}&limit=1"  # Solo traer el primer resultado
    
    response = requests.get(url)
    
    if response.status_code == 200:
        datos = response.json()  # Convertir la respuesta a formato JSON

        #Obtener la información del anime
        if 'data' in datos and len(datos['data']) > 0:
            anime = datos['data'][0]  # Tomar el primer resultado
            titulo = anime['title']
            url_anime = anime['url']
            sinopsis = anime['synopsis']
            imagen = anime['images']['jpg']['image_url']  # Imagen del anime
            calificacion = anime.get('score', 'N/A')  # Obtener la calificación (score), si no está disponible mostrar "N/A"

            # Inicializar el traductor
            translator = Translator()
            sinopsis_traducida = translator.translate(sinopsis, src='en', dest='es').text

            # Devolver los detalles del anime
            return titulo, sinopsis_traducida, url_anime, imagen, calificacion
        else:
            return None
    else:
        return None

#Función para obtener los 10 animes que están actualmente en emisión
def obtener_animes_recientes():
    url = "https://api.jikan.moe/v4/seasons/now"  #Obtener animes que están actualmente en emisión
    response = requests.get(url)

    if response.status_code == 200:
        datos = response.json()
        if 'data' in datos:
            #Limitar a los primeros 10 animes en emisión
            return [anime['title'] for anime in datos['data'][:10]]
        else:
            return None
    else:
        return None

#Función para obtener la lista de próximos estrenos de anime
def obtener_proximos_estrenos():
    url = "https://api.jikan.moe/v4/seasons/upcoming" 
    response = requests.get(url)
    if response.status_code == 200:
        datos = response.json()
        if 'data' in datos:
            return [anime['title'] for anime in datos['data'][:10]]
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
    async def ranime(self, ctx):
            #Obtener la recomendación de anime
            resultado = obtener_recomendacion_anime()

            if resultado:
                titulo, sinopsis_traducida, url_anime, imagen, calificacion  = resultado

                #Crear el embed
                embed = discord.Embed(
                    title=f"Recomendación de Anime: {titulo}",
                    description=sinopsis_traducida,
                    color=discord.Color.blue()  #Puedes cambiar el color del embed
                )
                embed.set_image(url=imagen)  #Añadir imagen al embed
                embed.add_field(name="Calificación", value=f"⭐ {calificacion}/10", inline=True)
                embed.add_field(name="Más detalles", value=f"[Ver más]({url_anime})", inline=False)

                #Enviar el embed en el canal
                await ctx.send(embed=embed)
            else:
                await ctx.send("No pude obtener una recomendación en este momento.")


    #Comando para buscar un anime específico
    @commands.command()
    async def sanime(self, ctx, *, query: str):
        resultado = buscar_anime(query)

        if resultado:
            titulo, sinopsis_traducida, url_anime, imagen, calificacion = resultado

            #Crear el embed
            embed = discord.Embed(
                title=f"Búsqueda de Anime: {titulo}",
                description=sinopsis_traducida,
                color=discord.Color.green()
            )
            embed.set_image(url=imagen)
            embed.add_field(name="Calificación", value=f"⭐ {calificacion}/10", inline=True)
            embed.add_field(name="Más detalles", value=f"[Ver más]({url_anime})", inline=False)

            #Enviar el embed en el canal
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No encontré resultados para **{query}**.")

    #Comando para obtener los 10 animes más recientes
    @commands.command()
    async def lanime(self, ctx):
        animes_recientes = obtener_animes_recientes()
        if animes_recientes:
            embed = discord.Embed(
                title="Aquí tienes una lista de los animes que están en emisión actualmente:",
                color=discord.Color.green()
            )
        
            #Crear una lista enumerada de los animes
            lista_animes = "\n".join([f"{i + 1}. {anime}" for i, anime in enumerate(animes_recientes)])
            embed.add_field(name="Lista de Animes", value=lista_animes, inline=False)
            embed.set_footer(text="¡Disfruta viendo anime!")  #Pie de página

            await ctx.send(embed=embed)
        else:
            await ctx.send("No pude obtener la lista de animes recientes en este momento.")
        
    #Comando para obtener la lista de próximos estrenos de anime
    @commands.command()
    async def animestrenos(self, ctx):
        proximos_estrenos = obtener_proximos_estrenos()
        if proximos_estrenos:
            embed = discord.Embed(title="Próximos estrenos de anime:", color=discord.Color.orange())
            lista_estrenos = "\n".join([f"{i + 1}. {anime}" for i, anime in enumerate(proximos_estrenos)])
            embed.add_field(name="Estrenos", value=lista_estrenos, inline=False)
            embed.set_footer(text="¡Disfruta viendo anime!")  #Pie de página

            await ctx.send(embed=embed)
        else:
            await ctx.send("No pude obtener la lista de próximos estrenos.")


#Asegúrate de que esta función se llama correctamente en tu bot
async def setup(bot):
    await bot.add_cog(Anime(bot))
