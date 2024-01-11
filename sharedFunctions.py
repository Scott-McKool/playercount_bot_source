from socket import gaierror, timeout
from time import time
import a2s

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
    