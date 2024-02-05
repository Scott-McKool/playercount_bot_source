from sharedFunctions import getServerInfo
from discord.ext import commands, tasks
from json import dump, loads
from config import Settings
import discord


class InfoTopic(commands.Cog):

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
    
    async def update_topic(self, address: tuple, channel: discord.channel):
        # get the given server's info
        info = getServerInfo(address)
        
        new_channel_topic = f"[server could not be contacted] ({address[0]}:{address[1]})"
        
        if info:
            new_channel_topic = f"[{info.player_count}/{info.max_players}] ■ {info.server_name} ■ {address[0]}:{address[1]}"

        # get the info currently displayed on the channel
        current_channel_topic = channel.topic
        # if the new topic is the same as the current topic don't bother editing ( to save on api calls )
        if new_channel_topic == current_channel_topic:
            return

        return await channel.edit(topic=new_channel_topic)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def infoTopic(self, ctx, address_string: str):
        '''Set this channel to display server info in the topic of the channel this command is run in'''

        address = await self.validateAddress(ctx, address_string)
        if not address:
            return
        
        # save this channel and the server it's dedicated to
        # make sure the file exists
        open("infoTopics.json", "a")

        # load the existing file
        with open("infoTopics.json", "rt") as inFile:
            text = inFile.read()
            # if the file is empty replace it with an empty dict so that it is valid for loads()
            if not text:
                text = "{}"
            channels: dict = loads(text)

        # add this channel to the data
        channels[str(ctx.channel.id)] = address

        # write back to the file
        with open("infoTopics.json", "wt") as outFile:
            dump(channels, outFile, indent=4)

        await ctx.send(f"chnnel topic now set to track {address}")

        try:
            await self.update_topic(address, ctx.channel)
        except discord.RateLimited:
            await ctx.send(f"command was sucessful, but rate limit prevents changes from being shown")


    @tasks.loop(seconds=Settings.Topics.REFRESH_TIME)
    async def update_info_topics(self):
        # make sure the file exists
        open("infoTopics.json", "a")
        # read the file of all the info channels
        with open("infoTopics.json", "rt") as inFile:
            text = inFile.read()
            if not text:
                text = "{}"
            channels: dict = loads(text)
        
        # for every channel with a info topic
        for channel_id, channel_info in channels.items():
            channel: discord.channel
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except (discord.errors.NotFound, discord.errors.Forbidden):
                    print(f"could not find channel {channel_id}, deleting it from tracked channels list. . .")
                    channels.pop(str(channel_id))

                    # write any changes made back to the file
                    with open("infoTopics.json", "wt") as outFile:
                        dump(channels, outFile, indent=4)

                    # call the function again to sort out the rest of the messages
                    # must do this instead of using 'continue' because the contents of the 
                    # channels dict has changed
                    return await self.update_info_topics()

            address = channel_info
            address = tuple(address)
            
            await self.update_topic(address, channel)


    @commands.Cog.listener()
    async def on_ready(self):
        self.update_info_topics.start()
        print("Info Topics Cog is ready")

async def setup(client):
    await client.add_cog(InfoTopic(client))