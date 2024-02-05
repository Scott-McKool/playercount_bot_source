from sharedFunctions import getServerInfo
from discord.ext import commands
from json import dump, loads
import discord

def makeServerEmbed(address):
    '''returns a discord.Embed object that summarizes a server's info for use in messages.'''

    info = getServerInfo(address)
    if info is None:
        
        embed = discord.Embed(title=f"Could not contact server", colour=discord.Colour.red())
        embed.set_footer(text=f"{address[0]}:{address[1]}")
        return embed

    embed = discord.Embed(title=f"{info.server_name}", colour=discord.Colour.blue())
    embed.add_field(name=f"{info.player_count}/{info.max_players} currently playing", value = f"map: {info.map_name}", inline=False)
    embed.set_footer(text=f"{address[0]}:{address[1]}")
    return embed

class MarkedChannels(commands.Cog):

    def __init__(self, client) -> None:
        super().__init__()
        self.bot = client

    async def validateAddress(self, ctx, route: str):
        try:
            ip, port = route.split(":")
            port = int(port)
        except ValueError:
            await ctx.send(f"Could not parse \"{route}\" the server should be formatted as [server url or ip]:[port]")
            return None
        return (ip,port)

    @commands.command(aliases=['join'])
    async def server(self, ctx):

        # make sure the file exists
        open("markedChannels.json", "a")

        # load the existing file
        with open("markedChannels.json", "rt") as inFile:
            text = inFile.read()
            # if the file is empty replace it with an empty dict so that it is valid for loads()
            if not text:
                text = "{}"
            channels: dict = loads(text)

        # look for the current channel in the file
        address = channels.get(str(ctx.channel.id), None)
        
        if not address:
            await ctx.send("This channel is not tracking any server")
            return
        
        embed = makeServerEmbed(tuple(address))

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def markChannel(self, ctx, address_string: str):
        '''Set the channel it's sent is as a channel for a given server.
        When users use the server command in a marked channel, the bot will
        post a message with the server's current info.'''

        address = await self.validateAddress(ctx, address_string)
        if not address:
            return
        
        # save this channel and the server it's dedicated to
        # make sure the file exists
        open("markedChannels.json", "a")

        # load the existing file
        with open("markedChannels.json", "rt") as inFile:
            text = inFile.read()
            # if the file is empty replace it with an empty dict so that it is valid for loads()
            if not text:
                text = "{}"
            channels: dict = loads(text)

        # add this channel to the data
        channels[str(ctx.channel.id)] = address

        # write back to the file
        with open("markedChannels.json", "wt") as outFile:
            dump(channels, outFile, indent=4)

        await ctx.send(f"channel now set to track {address}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("MarkedChannels Cog is ready")

async def setup(client):
    await client.add_cog(MarkedChannels(client))