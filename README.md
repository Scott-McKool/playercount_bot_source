# playercount bot
Basic bot that utilises python-a2s to display the playercount of servers running source games (gmod, counter strike, tf2, etc. . .)

## Features

### Display server info in a message
Creates a message that will update to display server name, player count, and map.<br>
Usage: `%infoMessage address:port` <br>
![image](https://github.com/Scott-McKool/playercount_bot_source/assets/44004555/c759c0b6-2ece-4f75-be85-b624370736ba)
![image](https://github.com/Scott-McKool/playercount_bot_source/assets/44004555/3002de20-4774-4161-9741-6db1cc13991f)


### Display server info in a category
Creates a category that will display the server's current playercount and have a custom name. <br>
Usage: `%infoCategory address:port custom name`<br>
![image](https://github.com/Scott-McKool/playercount_bot_source/assets/44004555/7c586b87-0d17-4b39-ae3e-d0f58fba08cb)
![image](https://github.com/Scott-McKool/playercount_bot_source/assets/44004555/8e4b7e31-9ee1-433b-bffa-3e18ecb35b5e)

### Display server info in the topic of a channel
When this command is sent in a text channel, the topic of the channel will display the playercount and server name. <br>
Usage `%infoTopic address:port` <br>
![image](https://github.com/Scott-McKool/playercount_bot_source/assets/44004555/6822f865-4d6a-4dce-bf88-c883fdd4247a)
![image](https://github.com/Scott-McKool/playercount_bot_source/assets/44004555/cffc1ed0-a44b-4a8c-8f18-84c187079d6d)


## Steps To Install
This has only been tested on ubuntu and raspberry pi OS, though it should work for all debian based distributions that have apt (and systemd for running on startup). <br>

This install script requires that you already have a bot registered with discord and have access to the bot token. <br>
You can make a bot/access its token at https://discord.com/developers/applications<br>

Clone the source code & run the install script.
```
git clone https://github.com/Scott-McKool/playercount_bot_source.git
cd playercount_bot_source/
./install.sh

```
