import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Guardar la instancia del bot

    #Configuración para yt-dlp
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
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'  #No extrae el video, solo el audio
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    #Esta lista contendrá las canciones que se van a reproducir
    song_queue = []  #Cola de canciones

    class Song:
        def __init__(self, title, url, requester):
            self.title = title
            self.url = url
            self.requester = requester

    class YTDLSource(discord.PCMVolumeTransformer):
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')  #Título de la canción
            self.url = data.get('url')  #URL del archivo de audio

        @classmethod
        async def from_url(cls, url, *, loop=None, stream=False):
            loop = loop or asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: Music.ytdl.extract_info(url, download=not stream))

            if 'entries' in data:
                data = data['entries'][0]

            filename = data['url'] if stream else Music.ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **Music.ffmpeg_options), data=data)

    async def play_next(self, ctx):
        #Función para reproducir la siguiente canción de la cola
        if len(self.song_queue) > 0:
            next_song = self.song_queue[0]
            player = await self.YTDLSource.from_url(next_song.url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))

            await ctx.send(f'🎶 **{player.title}** solicitada por {next_song.requester.mention} está sonando ahora.')

            self.song_queue.pop(0)
        else:
            await ctx.send("La cola de canciones está vacía.")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} está conectado")

    #Comando para hacer que el bot se una al canal de voz
    @commands.command()
    async def joinch(self, ctx):
        if ctx.author.voice:
            #Obtiene el canal de voz del usuario y se une
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f'Conectado al canal: {channel}')
        else:
            await ctx.send("¡Debes estar en un canal de voz para que el bot se una!") 

    #Comando para hacer que el bot se desconecte del canal de voz
    @commands.command()
    async def leavech(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Me he desconectado del canal de voz.")
        else:
            await ctx.send("No estoy conectado a ningún canal de voz.")

    #Comando para reproducir una canción desde una búsqueda o URL
    @commands.command(aliases=['p'])
    async def play(self, ctx, *, search: str):
        if ctx.voice_client:
            # Verifica si el usuario está en el mismo canal de voz que el bot
            if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
                async with ctx.typing():
                    try:
                        player = await self.YTDLSource.from_url(search, loop=self.bot.loop, stream=True)
                        self.song_queue.append(self.Song(title=player.title, url=search, requester=ctx.author))
                        if not ctx.voice_client.is_playing():
                            await self.play_next(ctx)
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
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Canción pausada.")
        else:
            await ctx.send("No hay ninguna canción reproduciéndose.")

    #Comando para reanudar la reproducción de una canción pausada
    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Canción reanudada.")
        else:
            await ctx.send("No hay ninguna canción pausada.")
            
    #Comando para saltar la canción actual y reproducir la siguiente
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await self.play_next(ctx)
            await ctx.send("Canción saltada.")
        else:
            await ctx.send("No hay ninguna canción reproduciéndose.")

    #Comando para ver las canciones en la cola
    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        songs_per_page = 5  #Número de canciones por página
        total_songs = len(self.song_queue)
        total_pages = (total_songs + songs_per_page - 1) // songs_per_page  #Calcular total de páginas

        #Validar si la página solicitada es válida
        if page < 1 or page > total_pages:
            await ctx.send(f"Página no válida. Hay un total de {total_pages} páginas.")
            return

        if total_songs > 0:
            start_index = (page - 1) * songs_per_page
            end_index = min(start_index + songs_per_page, total_songs)

            embed = discord.Embed(title="Cola de Canciones", color=discord.Color.blue())

            #Agregar las canciones a la descripción del embed
            for i, song in enumerate(self.song_queue[start_index:end_index]):
                embed.add_field(name=f"{start_index + i + 1}. **{song.title}**", value=f"Solicitada por {song.requester.mention}", inline=False)

            embed.set_footer(text=f"Página {page}/{total_pages} - Total: {total_songs} canciones.")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("La cola de canciones está vacía.")

    #Comando para eliminar una canción de la cola
    @commands.command()
    async def delete(self, ctx, position: int):
        if 1 <= position <= len(self.song_queue):
            removed_song = self.song_queue.pop(position - 1)
            await ctx.send(f"Se eliminó **{removed_song.title}** de la cola.")
        else:
            await ctx.send("¡Posición no válida! Por favor, ingresa un número válido.")

    #Comando para borrar toda la cola de canciones
    @commands.command()
    async def delall(self, ctx):
        self.song_queue.clear()  #Limpia toda la cola de canciones
        await ctx.send("La cola de canciones ha sido borrada.")

#Asegúrate de que esta función se llama correctamente en tu bot
async def setup(bot):
    await bot.add_cog(Music(bot))
