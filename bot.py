import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import Embed


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

#Comando "h" para que el bot nos de la informacion de comandos
@bot.command(aliases=['h'])
async def hola(ctx):
    rainbow_title = (
        "Comandos del Bot"
    )

    embed = Embed(title=rainbow_title, description="¡Hola! Soy un bot y me llegas altamente al pincho. Aquí tienes mis comandos:", color=0x00ff00)
    
    # Agregar campos con estilos mejorados
    embed.add_field(name="**!joinch**", value=":loudspeaker: Conecta al canal de voz", inline=False)
    embed.add_field(name="**!leavech**", value=":wave: Desconecta del canal de voz", inline=False)
    embed.add_field(name="**!play <url>**", value=":musical_note: Reproduce una canción", inline=False)
    embed.add_field(name="**!pause**", value=":pause_button: Pausa la canción actual", inline=False)
    embed.add_field(name="**!resume**", value="Reanuda la canción actual", inline=False)
    embed.add_field(name="**!skip**", value=":next_track: Salta la canción actual", inline=False)
    embed.add_field(name="**!queue**", value=":clipboard: Muestra la cola de canciones", inline=False)
    embed.add_field(name="**!ranime**", value=":mag: Recomendar un anime al azar", inline=False)

    await ctx.send(embed=embed)