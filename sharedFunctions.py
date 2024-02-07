from socket import gaierror, timeout
from json import dump, loads
from time import time
import a2s

# this function is stored once and shared so what all the different cogs can benefit from using the same cache
# would've stored this in playerCountBot.py but that causes circular dependencies (the cogs are imported by playerCountBot.py)

# the cache stores the results from getServerInfo as well as a unix timestamp of then the data was read
#
#   { ("address", port) : (timestamp, {info}) } 
server_info_cache = {}

def getServerInfo(address: tuple, use_cache = True, cache_time = 30):
    '''Retuns the a2s info for a server and uses caching\n
    returns None if the server could not be reached.'''

    cached_info = server_info_cache.get(address, None)
    if cached_info and use_cache:
        # check if the data is recent enough to use
        if time() - cached_info[0] < cache_time:
            return cached_info[1]
    # if cached info was not returned, fetch new info
    try:
        info = a2s.info(address)
        # add new info to the cache
        server_info_cache[address] = (time(), info)
        return info
    except (gaierror, timeout):
        return None
    

async def validateAddress(ctx, route: str):
    '''Used for validating an address passed by a user in a command.
    a valid adress should be formatted as address:port'''
    try:
        ip, port = route.split(":")
        port = int(port)
    except ValueError:
        await ctx.send(f"Could not parse \"{route}\" the server should be formatted as [server url or ip]:[port]")
        return None
    return (ip,port)

# functions for reading and writing json files to reduce reused code
    
def json_read(filename: str) -> dict:
    '''takes in the filename of the json file and returns a dict of it's contents
    returns {} on a new or empty file'''
    # use append mode to make the file if it does not exist
    # but also don't change anything if it already exists
    open(filename, "a")

    # load the existing file
    with open(filename, "rt") as inFile:
        text = inFile.read()
        # if the file is empty replace it with an empty dict so that it is valid for loads()
        if not text:
            text = "{}"
        # return the json dict
        return loads(text)
    
def json_write(filename: str, data: dict):
    '''dump dict to a json formatted file'''
    with open(filename, "wt") as outFile:
        dump(data, outFile, indent=4)