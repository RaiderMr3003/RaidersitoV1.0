import discord
import requests
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.members = True

class Otros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} está conectado")

    #Comando para obtener una imagen random de pug (son graciosos)
    @commands.command()
    async def pug(self, ctx):
        #Hacer una solicitud a la API para obtener una imagen random de pug
        response = requests.get("https://dog.ceo/api/breed/pug/images/random")
        data = response.json()
        image_url = data["message"]
    
        #Enviar la imagen al canal de Discord
        await ctx.send(image_url)

    @commands.command()
    async def basura(self, ctx):
        guild = ctx.guild  # Obtiene el servidor donde se ejecuta el comando
        members = guild.members  # Lista de miembros del servidor
        random_member = random.choice(members)  # Selecciona un miembro al azar
    
        # Verifica si el miembro tiene un avatar y lo envía en un embed
        embed = discord.Embed(
            title="Basura aleatoria",
            description=f"¡Mira esta basura! 🤣",
            color=discord.Color.red()  # Puedes cambiar el color a lo que prefieras
        )

        # Si el miembro tiene avatar, agrega la imagen al embed
        if random_member.avatar:
            embed.set_image(url=random_member.avatar.url)
        else:
            embed.add_field(name="Aviso", value="Tal vez no sea tan basura.", inline=False)

        # Envía la mención primero y luego el embed
        await ctx.send(f"Aquí está la basura de {random_member.mention}")
        await ctx.send(embed=embed)

#Asegúrate de que esta función se llama correctamente en tu bot
async def setup(bot):
    await bot.add_cog(Otros(bot))
