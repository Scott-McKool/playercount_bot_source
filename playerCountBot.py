from sharedFunctions import getServerInfo
from discord.ext import commands, tasks
import playerCountBotConfig
from time import sleep
import discord
import asyncio
import urllib
import os

bot = commands.Bot(command_prefix=playerCountBotConfig.PREFIX, intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("playerCountBot ready")
    # if an address for the status exists, start tracking it
    if playerCountBotConfig.STATUS_SERVER_ADDRESS != "":
        change_status.start()

@tasks.loop(seconds=playerCountBotConfig.REFRESH_TIME)
async def change_status():
    # get the info 
    info = getServerInfo(playerCountBotConfig.STATUS_SERVER_ADDRESS)

    new_status: str = f"{info.player_count}/{info.max_players} currently playing"
    if info is None:
        new_status = "Could not contact server."

    return await bot.change_presence(activity=discord.Game(new_status))

@bot.command()
async def ping(ctx):
    '''
    Gets playerCountBot's latency 
    '''
    await ctx.send(f"pong {round(bot.latency*1000)}ms")

# load the cogs for this bot
for file_name in os.listdir(f"{playerCountBotConfig.BOT_DIR}cogs"):
    if(file_name.endswith(".py")):
        asyncio.run(bot.load_extension(f"cogs.{file_name[:-3]}"))

# wait till an internet connection is established before trying to login
#TODO this is kind of a hack-y solution, find a better way of running code when internet access is gained
while(True):
    try:
        # will throw an error if not on internet
        urllib.request.urlopen("http://google.com")
    except Exception as e:
        print("did not log in, not connected to internet, retrying in 10 seconds. . .")
        sleep(10)
        continue
    bot.run(playerCountBotConfig.DISCORD_TOKEN)
    break