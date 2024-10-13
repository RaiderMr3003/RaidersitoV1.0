import discord
from discord.ext import commands
from discord import Embed
from discord.ui import Button, View

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Aquí defines el commands_info directamente dentro del cog
        self.commands_info = {
            "Música": {
                "description": "Comandos relacionados con la música.",
                "commands": [
                    {"name": "!joinch", "description": "🔊 Conecta al canal de voz"},
                    {"name": "!leavech", "description": "👋 Desconecta del canal de voz"},
                    {"name": "!play o !p", "description": "🎵 Reproduce una canción"},
                    {"name": "!pause", "description": "⏸️ Pausa la canción actual"},
                    {"name": "!resume", "description": "▶️ Reanuda la canción actual"},
                    {"name": "!skip", "description": "⏭️ Salta la canción actual"},
                    {"name": "!queue o !q", "description": "📝 Muestra la cola de canciones"},
                    {"name": "!delete", "description": "🗑️ Elimina una canción de la cola"},
                    {"name": "!delall", "description": "🗑️ Elimina toda la cola de canciones"},
                ],
            },
            "Anime": {
                "description": "Comandos relacionados con anime.",
                "commands": [
                    {"name": "!ranime", "description": "🎲 Recomendar un anime Random"},
                    {"name": "!sanime", "description": "🔍 Buscar un anime específico"},
                    {"name": "!lanime", "description": "📄 Lista 10 animes que están en emisión"},
                ],
            },
            "Juegos": {
                "description": "Comandos relacionados con juegos.",
                "commands": [
                    {"name": "!juego", "description": "🎮 Descripción del comando de juego."},
                ],
            },
            "Moderación": {
                "description": "Comandos de moderación.",
                "commands": [
                    {"name": "!ping", "description": "🛜 Muestra la latencia de la conexión"},
                    {"name": "!delmsg", "description": "🗑️ Borra mensajes"},
                ],
            },
            "Otros": {
                "description": "Comandos otros.",
                "commands": [
                    {"name": "!pug", "description": "🐶 Muestra una foto de un pug."},
                    {"name": "!basura", "description": "🗑️ Muestra una foto de alguien random del servidor."},
                ],
            },
        }

    @commands.command(aliases=['h'])
    async def hola(self, ctx):
        view = View(timeout=60)

        # Crear botones para cada sección
        music_button = Button(label="Música", style=discord.ButtonStyle.primary, custom_id="Música")
        anime_button = Button(label="Anime", style=discord.ButtonStyle.primary, custom_id="Anime")
        games_button = Button(label="Juegos", style=discord.ButtonStyle.primary, custom_id="Juegos")
        mod_button = Button(label="Moderación", style=discord.ButtonStyle.primary, custom_id="Moderación")
        others_button = Button(label="Otros", style=discord.ButtonStyle.primary, custom_id="Otros")
        back_button = Button(label="Volver", style=discord.ButtonStyle.secondary, custom_id="Volver")

        # Agregar botones a la vista
        view.add_item(music_button)
        view.add_item(anime_button)
        view.add_item(games_button)
        view.add_item(mod_button)
        view.add_item(others_button)

        # Enviar mensaje inicial
        initial_message = await ctx.send("¡Hola! Soy Raidersito. Selecciona una sección para ver los comandos:", view=view)

        # Definir el comportamiento de los botones
        async def button_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("¡Solo puedes usar los botones que creaste!", ephemeral=True)
                return

            section = interaction.data['custom_id']

            embed = Embed(title=f"Comandos de {section}", color=0x00ff00)
            section_info = self.commands_info[section]

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

            # Limpiar la vista y agregar botones de sección nuevamente
            view.clear_items()
            view.add_item(music_button)
            view.add_item(anime_button)
            view.add_item(games_button)
            view.add_item(mod_button)
            view.add_item(others_button)

            await interaction.response.edit_message(content="¡Hola! Soy Raidersito. Selecciona una sección para ver los comandos:", embed=None, view=view)

        # Asociar el callback a los botones
        music_button.callback = button_callback
        anime_button.callback = button_callback
        games_button.callback = button_callback
        mod_button.callback = button_callback
        others_button.callback = button_callback
        back_button.callback = back_button_callback

# Cargar el cog
async def setup(bot):
    await bot.add_cog(Info(bot))
