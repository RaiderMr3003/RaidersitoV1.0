import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import Button, View
from discord import Embed
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

        #Añadir descripción de la sección
        embed.description = section_info["description"]

        #Añadir comandos de la sección
        for command in section_info["commands"]:
            embed.add_field(name=command["name"], value=command["description"], inline=False)

        #Limpiar la vista y agregar el botón de volver
        view.clear_items()
        view.add_item(back_button)

        #Editar el mensaje con el nuevo embed y la vista actualizada
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