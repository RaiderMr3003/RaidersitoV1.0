import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

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

#Cargar cogs
async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Iniciar el bot
async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

asyncio.run(main())