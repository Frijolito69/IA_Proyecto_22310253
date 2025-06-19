import discord

token = open("token.txt", "r").read()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True           
intents.presences = True        

def community_report(guild):
    online = 0
    idle = 0
    offline = 0

    for m in guild.members:
        if str(m.status) == "online":
            online += 1
        if str(m.status) == "offline":
            offline += 1
        else:
            idle += 1

    return online, idle, offline



client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {1385094640570466466}')


@client . event 
async  def  on_message ( message ):   # evento que ocurre por cada mensaje.
    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
    sentdex_guild  =  client . get_guild ( 1385104573340844113 )

    if "hola" in message.content.lower():
        await message.channel.send("HOLI")
    
    elif "numero.miembros" == message.content.lower():
        await message.channel.send(f"```{sentdex_guild.member_count}```")

    elif "bot.reporte_comunidad" == message.content.lower():
        online, idle, offline = community_report(sentdex_guild)
        await message.channel.send(f"```Online: {online}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")

    elif "bot.logout()" == message.content.lower():
        await client.close()
    
     

client.run(token)
