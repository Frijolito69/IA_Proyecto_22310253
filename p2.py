import random
import discord
import asyncio
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import os
import requests  

style.use("fivethirtyeight")

token = open("token.txt", "r").read().strip()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

class MyClient(discord.Client):
    async def setup_hook(self):
        self.loop.create_task(self.user_metrics_task())

    async def on_ready(self):
        self.sentdex_guild = discord.utils.get(self.guilds, id=1385104573340844113)

        if self.sentdex_guild is None:
            print(" ERROR: No se encontró el servidor con ese ID.")
        else:
            print(f" Bot conectado como {self.user}")
            print(f" Servidor detectado: {self.sentdex_guild.name} ({self.sentdex_guild.id})")

    async def on_message(self, message):
        if message.author == self.user:
            return

        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
        content = message.content.lower()

        if not hasattr(self, 'sentdex_guild') or self.sentdex_guild is None:
            self.sentdex_guild = discord.utils.get(self.guilds, id=1385104573340844113)

        if "hola" in content:
            await message.channel.send("HOLI")

        elif content == "numero.miembros":
            await message.channel.send(f"```{self.sentdex_guild.member_count}```")

        elif content == "bot.reporte_comunidad":
            online, idle, offline = self.community_report()
            await message.channel.send(
                f"```Online: {online}\nIdle/busy/dnd: {idle}\nOffline: {offline}```"
            )

        elif content == "bot.grafica":
            try:
                await message.channel.send(file=discord.File("online.png"))
            except Exception as e:
                await message.channel.send(" No se pudo enviar la gráfica.")
                print(f"Error al enviar la imagen: {e}")

        elif content == "bot.logout()":
            await self.close()

        elif content == "!dado":
            numero = random.randint(1, 6)
            await message.channel.send(f"🎲 Sacaste un {numero}")

        elif content.startswith("!votar"):
            mensaje = await message.channel.send("🗳️ Votación: ✅ = Sí / ❌ = No")
            await mensaje.add_reaction("✅")
            await mensaje.add_reaction("❌")

        elif content.startswith("!meme") or content.startswith("!imagen"):
            try:
                carpeta = "imagenes"
                imagenes = [f for f in os.listdir(carpeta) if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]

                if imagenes:
                    seleccionada = random.choice(imagenes)
                    ruta = os.path.join(carpeta, seleccionada)
                    await message.channel.send(file=discord.File(ruta))
                else:
                    await message.channel.send(" No hay imágenes en la carpeta 'imagenes'.")
            except Exception as e:
                await message.channel.send(" Ocurrió un error al enviar la imagen.")
                print(f"Error en !meme: {e}")

        elif content.startswith("!bitcoin"):
            try:
                moneda = "usd"
                if "mxn" in content:
                    moneda = "mxn"

                url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={moneda}"
                response = requests.get(url)
                data = response.json()

                if "bitcoin" in data and moneda in data["bitcoin"]:
                    precio = data["bitcoin"][moneda]
                    simbolo = "$" if moneda == "usd" else "MX$"
                    await message.channel.send(f"💰 El precio actual de **Bitcoin (BTC)** es: **{simbolo}{precio:,.2f} {moneda.upper()}**")
                else:
                    await message.channel.send(" No se pudo obtener el precio de Bitcoin.")

            except Exception as e:
                await message.channel.send(" Error al obtener el precio de Bitcoin.")
                print(f"Error en !bitcoin: {e}")

        elif content == "!ayuda" or content == "!comandos":
            ayuda = (
                "📌 **Lista de comandos disponibles:**\n"
                "• `hola` → El bot responde con un saludo\n"
                "• `numero.miembros` → Muestra el número de miembros del servidor\n"
                "• `bot.reporte_comunidad` → Reporte de usuarios online, inactivos y offline\n"
                "• `bot.grafica` → Muestra la gráfica del estado de los usuarios\n"
                "• `!dado` → Tira un dado virtual y te da un número entre 1 y 6\n"
                "• `!votar` → Crea una votación con ✅ y ❌\n"
                "• `!meme` o `!imagen` → Envía una imagen aleatoria de la carpeta `imagenes`\n"
                "• `!bitcoin` → Muestra el precio actual del Bitcoin en USD\n"
                "• `!bitcoin mxn` → Muestra el precio del Bitcoin en pesos mexicanos\n"
                "• `bot.logout()` → Apaga el bot (solo si tienes permiso)\n"
                "• `!ayuda` o `!comandos` → Muestra esta lista\n"
            )
            await message.channel.send(ayuda)

    def community_report(self):
        online = 0
        idle = 0
        offline = 0

        for m in self.sentdex_guild.members:
            status = str(m.status)
            if status == "online":
                online += 1
            elif status in ["idle", "dnd"]:
                idle += 1
            elif status == "offline":
                offline += 1

        return online, idle, offline

    async def user_metrics_task(self):
        await self.wait_until_ready()

        while not self.is_closed():
            try:
                if self.sentdex_guild is not None:
                    online, idle, offline = self.community_report()

                    with open("usermetrics.csv", "a") as f:
                        f.write(f"{int(time.time())},{online},{idle},{offline}\n")

                    # Actualizar gráfica
                    df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
                    df['date'] = pd.to_datetime(df['time'], unit='s')
                    df.drop("time", axis=1, inplace=True)
                    df.set_index("date", inplace=True)

                    plt.clf()
                    df[['online', 'idle', 'offline']].plot()
                    plt.title("Estado de Usuarios del Servidor")
                    plt.xlabel("Tiempo")
                    plt.ylabel("Cantidad")
                    plt.legend()
                    plt.tight_layout()
                    plt.savefig("online.png")

                await asyncio.sleep(5)

            except Exception as e:
                print(f"Error en metrics: {e}")
                await asyncio.sleep(5)

client = MyClient(intents=intents)
client.run(token)
