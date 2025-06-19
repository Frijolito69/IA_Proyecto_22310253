import discord
import asyncio
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style

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

        if not hasattr(self, 'sentdex_guild') or self.sentdex_guild is None:
            self.sentdex_guild = discord.utils.get(self.guilds, id=1385104573340844113)

        if "hola" in message.content.lower():
            await message.channel.send("HOLI")

        elif message.content.lower() == "numero.miembros":
            await message.channel.send(f"```{self.sentdex_guild.member_count}```")

        elif message.content.lower() == "bot.reporte_comunidad":
            online, idle, offline = self.community_report()
            await message.channel.send(
                f"```Online: {online}\nIdle/busy/dnd: {idle}\nOffline: {offline}```"
            )

        elif message.content.lower() == "bot.grafica":
            try:
                await message.channel.send(file=discord.File("online.png"))
            except Exception as e:
                await message.channel.send(" No se pudo enviar la gráfica.")
                print(f"Error al enviar la imagen: {e}")

        elif message.content.lower() == "bot.logout()":
            await self.close()

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
