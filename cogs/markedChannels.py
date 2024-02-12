from sharedFunctions import getServerInfo, json_read, json_write, validate_address, admin_only
from discord.ext import commands
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

    @commands.command(aliases=['join'])
    async def server(self, ctx):

        channels: dict = json_read("markedChannels.json")

        # look for the current channel in the file
        address = channels.get(str(ctx.channel.id), None)
        
        if not address:
            await ctx.send("This channel is not tracking any server")
            return
        
        embed = makeServerEmbed(tuple(address))

        await ctx.send(embed=embed)

    @commands.command()
    @validate_address
    @admin_only
    async def markChannel(self, ctx, address_string: str):
        '''Set the channel it's sent is as a channel for a given server.
        When users use the server command in a marked channel, the bot will
        post a message with the server's current info.'''

        address = address_string.split(":")
        address = (address[0], int(address[1]))
        
        channels: dict = json_read("markedChannels.json")

        # add this channel to the data
        channels[str(ctx.channel.id)] = address

        json_write("markedChannels.json", channels)

        await ctx.send(f"channel now set to track {address}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("MarkedChannels Cog is ready")

async def setup(client):
    await client.add_cog(MarkedChannels(client))