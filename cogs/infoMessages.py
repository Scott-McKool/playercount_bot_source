from sharedFunctions import getServerInfo
from discord.ext import commands, tasks
from json import dump, loads
from config import Settings
import discord
import a2s

def makeServerEmbed(address):
    '''returns a discord.Embed object that summarizes a server's info for use in messages.'''

    info = getServerInfo(address)
    if info is None:
        
        embed = discord.Embed(title=f"Could not contact server", colour=discord.Colour.red())
        embed.set_footer(text=f"{address[0]}:{address[1]}\nData updates every {Settings.Messages.REFRESH_TIME} seconds")
        return embed

    embed = discord.Embed(title=f"{info.server_name}", colour=discord.Colour.blue())
    embed.add_field(name=f"{info.player_count}/{info.max_players} currently playing", value = "", inline=False)
    embed.set_footer(text=f"{address[0]}:{address[1]}\nData updates every {Settings.Messages.REFRESH_TIME} seconds")
    return embed

class InfoMessages(commands.Cog):

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
        
    @commands.command()
    async def info(self, ctx, route : str):
        address = await self.validateAddress(ctx, route)
        if not address:
            return
        info = a2s.info(address)
        return await ctx.send(f"{str(info)}")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def infoMessage(self, ctx, address_string: str):
        '''Makes an embed that will auto update information about a server'''
        address = await self.validateAddress(ctx, address_string)
        if not address:
            return
        
        # make the embed for displaying the server info
        embed = makeServerEmbed(address)

        # join_button = discord.ui.Button(label="join the server", url=f"steam://connect/{address[0]}:{address[1]}", style=discord.ButtonStyle.link)
        # view = discord.ui.View()
        # view.add_item(join_button)

        # only returns temporary message, need to save id to update in the future
        persist_message = await ctx.send(embed=embed)#, view=view) 
        
        # save this message in a file to keep track of it
        # a json text file that stores a dict of servers>channels>messages
        # make sure the file exists
        open("infoMessages.json", "a")

        # load the existing file
        with open("infoMessages.json", "rt") as inFile:
            text = inFile.read()
            # if the file is empty replace it with an empty dict so that it is valid for loads()
            if not text:
                text = "{}"
            messages = loads(text)

        # add this message to the data
        if not str(persist_message.guild.id) in messages:
            messages[str(persist_message.guild.id)] = {}

        if not str(persist_message.channel.id) in messages[str(persist_message.guild.id)]:
            messages[str(persist_message.guild.id)][str(persist_message.channel.id)] = {}

        messages[str(persist_message.guild.id)][str(persist_message.channel.id)][str(persist_message.id)] = address

        # write back to the file
        with open("infoMessages.json", "wt") as outFile:
            dump(messages, outFile, indent=4)

        # delete the message command
        await ctx.message.delete(delay=1.5)

    @tasks.loop(seconds=Settings.Messages.REFRESH_TIME)
    async def update_info_messages(self):
        # make sure the file exists
        open("infoMessages.json", "a")
        # read the file of all the info messages
        with open("infoMessages.json", "rt") as inFile:
            text = inFile.read()
            if not text:
                text = "{}"
            messages: dict = loads(text)
            
        #TODO: find a better way of looping through the stored messages

        # loop through every stored message
        guilds_dict: dict
        guild_id: int
        for guild_id, guilds_dict in messages.items():
            channels_dict: dict
            channel_id: int

            for channel_id, channels_dict in guilds_dict.items():
                message_id: int
                message_address: list
                message_channel: discord.channel
                try:
                    message_channel = await self.bot.fetch_channel(channel_id)
                except discord.errors.NotFound as e:
                    print(e)
                    print(f"could not find channel {channel_id}, deleting it from tracked message list. . .")
                    messages[str(guild_id)].pop(str(channel_id))

                    # write any changes made back to the file
                    with open("infoMessages.json", "wt") as outFile:
                        dump(messages, outFile, indent=4)

                    # call the function again to sort out the rest of the messages
                    return await self.update_info_messages()
                
                for message_id, message_address in channels_dict.items():
                    message:discord.message
                    try:
                        message = await message_channel.fetch_message(message_id)
                    except discord.errors.NotFound as e:
                        print(e)
                        print(f"could not find message {message_id}, deleting it from tracked message list. . .")
                        messages[str(guild_id)][str(channel_id)].pop(message_id)

                        # write any changes made back to the file
                        with open("infoMessages.json", "wt") as outFile:
                            dump(messages, outFile, indent=4)

                        # call the function again to sort out the rest of the messages
                        return await self.update_info_messages()

                    else:
                    
                        # retreive new info about the server
                        address = (message_address[0], message_address[1])
                        # update message with new info
                        # make a new embed for the message
                        embed = makeServerEmbed(address)
                        # get the message's current content
                        current_embed = message.embeds[0]
                        # only edit the message if the new embed is different from the old one
                        if current_embed == embed:
                            continue
                        # edit the message
                        await message.edit(embed=embed)


    @commands.Cog.listener()
    async def on_ready(self):
        self.update_info_messages.start()
        print("Messages Cog is ready")

async def setup(client):
    await client.add_cog(InfoMessages(client))