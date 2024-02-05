from sharedFunctions import getServerInfo
from discord.ext import commands, tasks
from json import dump, loads
from config import Settings
import discord

#TODO: find a better way to stay under or deal with the api rate limit for updating a channel name ( twice per 10 mins )

class InfoCategories(commands.Cog):

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
    @commands.has_permissions(administrator = True)
    async def infoCategory(self, ctx, address_string: str, *server_name):
        '''Make a category who's name is the given server's player count'''
        address = await self.validateAddress(ctx, address_string)
        if not address:
            return
        # get the given server's info
        info = getServerInfo(address)
        
        category_name = "Could not contact server"
        server_name = ' '.join(server_name)
        
        if info:
            category_name = f"[{info.player_count}/{info.max_players}] {server_name}"

        # make the text category
        guild = ctx.guild
        category = await guild.create_category(category_name, 
                                                  reason=f"player count tracking category made by {ctx.author}")
        
        # save this message in a file to keep track of it
        # a json text file that stores a dict of categories
        # make sure the file exists
        open("infoCategories.json", "a")

        # load the existing file
        with open("infoCategories.json", "rt") as inFile:
            text = inFile.read()
            # if the file is empty replace it with an empty dict so that it is valid for loads()
            if not text:
                text = "{}"
            categories = loads(text)


        # save the category name and address
        categories[str(category.id)] = (address, server_name)

        # write back to the file
        with open("infoCategories.json", "wt") as outFile:
            dump(categories, outFile, indent=4)

        # delete the message command
        await ctx.message.delete(delay=1.5)
                

    @tasks.loop(seconds=Settings.Categories.REFRESH_TIME)
    async def update_info_categories(self):
        # make sure the file exists
        open("infoCategories.json", "a")
        # read the file of all the info categories
        with open("infoCategories.json", "rt") as inFile:
            text = inFile.read()
            if not text:
                text = "{}"
            categories: dict = loads(text)

        # for every category
        category_id: int
        category_info: tuple
        for category_id, category_info in categories.items():

            category: discord.CategoryChannel
            try:
                category = await self.bot.fetch_channel(category_id)
            except discord.errors.NotFound as e:
                    print(e)
                    print(f"could not find category {category_id}, deleting it from tracked categories list. . .")
                    categories.pop(category_id)

                    # write any changes made back to the file
                    with open("infoCategories.json", "wt") as outFile:
                        dump(categories, outFile, indent=4)

                    # call the function again to sort out the rest of the messages
                    return await self.update_info_categories()

            address, server_name  = category_info
            address = tuple(address)
            # get the given server's info
            info = getServerInfo(address)
            
            new_category_name = f"[offline]] {server_name}"
            
            if info:
                new_category_name = f"[{info.player_count}/{info.max_players}] {server_name}"

            # get the info currently displayed on the category
            current_category_name = category.name
            # if the new name is the same as the current name don't bother editing the name ( to save on api calls )
            if new_category_name == current_category_name:
                continue

            await category.edit(name=new_category_name)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_info_categories.start()
        print("categories Cog is ready")

async def setup(client):
    await client.add_cog(InfoCategories(client))