import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import Button, View
from discord import Embed
import yt_dlp as youtube_dl
import asyncio
from commands.commands_info import commands_info

# Cargamos el archivo .env donde se encuentra el token del bot
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Creamos el bot el cual usara "!" para activar los comandos
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

#Este sera el evento que nos avisara si el bot se ha conectado correctamente
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    print('------')


#INFO
#Comando "h" para que el bot nos dé la información de comandos
@bot.command(aliases=['h'])
async def hola(ctx):
    view = View(timeout=60)  #Tiempo de espera para la interacción

    #Crear botones para cada sección
    music_button = Button(label="Música", style=discord.ButtonStyle.primary, custom_id="Música")
    anime_button = Button(label="Anime", style=discord.ButtonStyle.primary, custom_id="Anime")
    games_button = Button(label="Juegos", style=discord.ButtonStyle.primary, custom_id="Juegos")
    mod_button = Button(label="Moderación", style=discord.ButtonStyle.primary, custom_id="Moderación")
    others_button = Button(label="Varios", style=discord.ButtonStyle.primary, custom_id="Varios")
    back_button = Button(label="Volver", style=discord.ButtonStyle.secondary, custom_id="Volver")
    
    #Agregar botones a la vista
    view.add_item(music_button)
    view.add_item(anime_button)
    view.add_item(games_button)
    view.add_item(mod_button)
    view.add_item(others_button)

    #Enviar mensaje inicial
    initial_message = await ctx.send("¡Hola! Soy Raidersito. Selecciona una sección para ver los comandos:", view=view)

    #Definir el comportamiento de los botones
    async def button_callback(interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("¡Solo puedes usar los botones que creaste!", ephemeral=True)
            return

        section = interaction.data['custom_id']

        embed = Embed(title=f"Comandos de {section}", color=0x00ff00)
        section_info = commands_info[section]

        # Añadir descripción de la sección
        embed.description = section_info["description"]

        # Añadir comandos de la sección
        for command in section_info["commands"]:
            embed.add_field(name=command["name"], value=command["description"], inline=False)

        # Limpiar la vista y agregar el botón de volver
        view.clear_items()
        view.add_item(back_button)

        # Editar el mensaje con el nuevo embed y la vista actualizada
        await interaction.response.edit_message(embed=embed, view=view)

    async def back_button_callback(interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("¡Solo puedes usar los botones que creaste!", ephemeral=True)
            return

        #Limpiar la vista y agregar botones de sección nuevamente
        view.clear_items()
        view.add_item(music_button)
        view.add_item(anime_button)
        view.add_item(games_button)
        view.add_item(mod_button)
        view.add_item(others_button)

        await interaction.response.edit_message(content="¡Hola! Soy Raidersito. Selecciona una sección para ver los comandos:", embed=None, view=view)

    #Asociar el callback a los botones
    music_button.callback = button_callback
    anime_button.callback = button_callback
    games_button.callback = button_callback
    mod_button.callback = button_callback
    others_button.callback = button_callback
    back_button.callback = back_button_callback


#MUSICA
#Configuración para yt-dlp
#Estas son las opciones que se usarán para extraer audio de YouTube usando yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',  
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True, 
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

#Configuración para ffmpeg
#Estas son las opciones que se usarán para reproducir audio con ffmpeg
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'  # No extrae el video, solo el audio
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

#Esta lista contendrá las canciones que se van a reproducir
#Clase que maneja las canciones en la cola
class Song:
    def __init__(self, title, url, requester):
        self.title = title
        self.url = url
        self.requester = requester

#Cola de canciones
song_queue = []

#Clase que maneja la reproducción de audio extraído usando yt-dlp
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')  # Título de la canción
        self.url = data.get('url')  # URL del archivo de audio

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

#Función para reproducir la siguiente canción de la cola
async def play_next(ctx):
    if len(song_queue) > 0:
        next_song = song_queue[0]
        player = await YTDLSource.from_url(next_song.url, loop=bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: bot.loop.create_task(play_next(ctx)))

        await ctx.send(f'🎶 **{player.title}** solicitada por {next_song.requester.mention} está sonando ahora.')

        song_queue.pop(0)
    else:
        await ctx.send("La cola de canciones está vacía.")

#Comando para hacer que el bot se una al canal de voz
@bot.command()
async def joinch(ctx):
    if ctx.author.voice:
        # Obtiene el canal de voz del usuario y se une
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Conectado al canal: {channel}')
    else:
        await ctx.send("¡Debes estar en un canal de voz para que el bot se una!") 

#Comando para hacer que el bot se desconecte del canal de voz
@bot.command()
async def leavech(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Me he desconectado del canal de voz.")
    else:
        await ctx.send("No estoy conectado a ningún canal de voz.")

#Comando para reproducir una canción desde una búsqueda o URL
@bot.command(aliases=['p'])
async def play(ctx, *, search: str):
    if ctx.voice_client:
        #Verifica si el usuario está en el mismo canal de voz que el bot
        if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
            async with ctx.typing():
                try:
                    player = await YTDLSource.from_url(search, loop=bot.loop, stream=True)
                    song_queue.append(Song(title=player.title, url=search, requester=ctx.author))
                    if not ctx.voice_client.is_playing():
                        await play_next(ctx)
                    else:
                        await ctx.send(f'Se agregó a la cola: **{player.title}** solicitada por {ctx.author.mention}')
                except youtube_dl.utils.DownloadError as e:
                    await ctx.send(f"Ocurrió un error al intentar reproducir la canción: {str(e)}")
                except Exception as e:
                    await ctx.send(f"Ocurrió un error inesperado: {str(e)}")
        else:
            await ctx.send("¡Debes estar en el mismo canal de voz que yo para solicitar canciones!")
    else:
        await ctx.send("¡Primero debes hacer que me una a un canal de voz usando **!joinch**")

#Comando para pausar la reproducción de la canción actual
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Canción pausada.")
    else:
        await ctx.send("No hay ninguna canción reproduciéndose.")

#Comando para reanudar la reproducción de una canción pausada
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Canción reanudada.")
    else:
        await ctx.send("No hay ninguna canción pausada.")

#Comando para saltar la canción actual y reproducir la siguiente
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await play_next(ctx)
        await ctx.send("Canción saltada.")
    else:
        await ctx.send("No hay ninguna canción reproduciéndose.")

#Comando para ver las canciones en la cola
@bot.command(aliases=['q'])
async def queue(ctx, page: int = 1):
    songs_per_page = 5  #Número de canciones por página
    total_songs = len(song_queue)
    total_pages = (total_songs + songs_per_page - 1) // songs_per_page  #Calcular total de páginas

    #Validar si la página solicitada es válida
    if page < 1 or page > total_pages:
        await ctx.send(f"Página no válida. Hay un total de {total_pages} páginas.")
        return

    if total_songs > 0:
        start_index = (page - 1) * songs_per_page
        end_index = min(start_index + songs_per_page, total_songs)

        embed = Embed(title="Cola de Canciones", color=0x00ff00)

        #Agregar las canciones a la descripción del embed
        for i, song in enumerate(song_queue[start_index:end_index]):
            embed.add_field(name=f"{start_index + i + 1}. **{song.title}**", value=f"Solicitada por {song.requester.mention}", inline=False)

        embed.set_footer(text=f"Página {page}/{total_pages} - Total: {total_songs} canciones.")
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("La cola de canciones está vacía.")

#Comando para eliminar una canción de la cola
@bot.command()
async def delete(ctx, position: int):
    if 1 <= position <= len(song_queue):
        removed_song = song_queue.pop(position - 1)
        await ctx.send(f"Se eliminó **{removed_song.title}** de la cola.")
    else:
        await ctx.send("¡Posición no válida! Por favor, ingresa un número válido.")

#Comando para borrar toda la cola de canciones
@bot.command()
async def delall(ctx):
    global song_queue 
    song_queue.clear()  #Limpia toda la cola de canciones
    await ctx.send("La cola de canciones ha sido borrada.")


# Iniciar el bot
bot.run(TOKEN)