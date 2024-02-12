#!bot_venv/bin/python3

from discord.ext.commands.errors import CheckFailure
from sharedFunctions import getServerInfo
from discord.ext import commands, tasks
from config import Settings
from os import listdir
from time import sleep
import discord
import asyncio
import urllib

bot = commands.Bot(command_prefix=Settings.PREFIX, intents=discord.Intents.all(), max_ratelimit_timeout=30)

@bot.event
async def on_ready():
    print("playerCountBot ready")
    # if an address for the status exists, start tracking it
    if Settings.Status.SERVER_ADDRESS != None:
        change_status.start()

@tasks.loop(seconds=Settings.Status.REFRESH_TIME)
async def change_status():
    # get the info 
    info = getServerInfo(Settings.Status.SERVER_ADDRESS)

    new_status = "Could contact server."
    if info:
        new_status: str = f"{info.player_count}/{info.max_players} currently playing."

    return await bot.change_presence(activity=discord.Game(new_status))

@bot.command()
async def ping(ctx):
    '''
    Gets playerCountBot's latency 
    '''
    await ctx.send(f"pong {round(bot.latency*1000)}ms")

@bot.event
async def on_command_error(ctx, error):
    # silence all check failures
    if isinstance(error, CheckFailure):
        return
    # anything else gets raised
    raise(error)

# load the cogs for this bot
for file_name in listdir(f"{Settings.BOT_DIR}cogs"):
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
    bot.run(Settings.DISCORD_TOKEN)
    break