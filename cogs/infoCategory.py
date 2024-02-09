from sharedFunctions import getServerInfo, json_read, json_write, validateAddress, admin_check
from discord.ext import commands, tasks
from config import Settings
import discord

#TODO: find a better way to stay under or deal with the api rate limit for updating a channel name ( twice per 10 mins )

class InfoCategories(commands.Cog):

    def __init__(self, client) -> None:
        super().__init__()
        self.bot = client
    
    @commands.command()
    async def infoCategory(self, ctx, address_string: str, *server_name):
        '''Make a category who's name is the given server's player count'''
        if not await admin_check(ctx):
            return

        address = await validateAddress(ctx, address_string)
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
        categories: dict = json_read("infoCategories.json")

        # save the category name and address
        categories[str(category.id)] = (address, server_name)

        # write back to the file
        json_write("infoCategories.json", categories)

        # delete the message command
        await ctx.message.delete(delay=1.5)
                

    @tasks.loop(seconds=Settings.Categories.REFRESH_TIME)
    async def update_info_categories(self):

        categories: dict = json_read("infoCategories.json")

        # for every category
        category_id: int
        category_info: tuple
        for category_id, category_info in categories.items():

            category: discord.CategoryChannel
            try:
                category = await self.bot.fetch_channel(category_id)
            except (discord.errors.NotFound, discord.errors.Forbidden):
                    print(f"could not find category {category_id}, deleting it from tracked categories list. . .")
                    categories.pop(str(category_id))

                    # write any changes made back to the file
                    json_write("infoCategories.json", categories)

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

            try:
                await category.edit(name=new_category_name)
            except discord.RateLimited:
                print(f"Rate limited when updating category {category_id}, skipping for now. . .")
                continue

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_info_categories.start()
        print("categories Cog is ready")

async def setup(client):
    await client.add_cog(InfoCategories(client))