#!/bin/sh

# check for root (user id of 0)
 [ `id -u` -eq 0 ] && echo "this script should not be run as root" && exit 1

# get discord token from user
echo "get the bot's token from the discord dev portal and enter it here: "
read DISCORDTOKEN 

# make a config file for inportant variables
echo "creating config file 'playerCountBotConfig.py'"
    cat > playerCountBotConfig.py <<CONFIGFILE
### user settings
# time in seconds for what nterval to refresh server info
REFRESH_TIME = 60 
PREFIX = "%"
# if supplied, the address to be tracked for the bot's status
STATUS_SERVER_ADDRESS = None # example: ("1.2.3.4",27015)
### bot constants
DISCORD_TOKEN = "$DISCORDTOKEN"
BOT_DIR = "$PWD/"
CONFIGFILE
# change permisssions of config file so that other users may not read it
chmod 660 playerCountBotConfig.py

### install requirements
echo "installing pip with apt. . ."
sudo apt update && sudo apt install python3-pip -y || { echo "failed to install python3-pip, aborting. . ."; exit 1; }

# install python packages
echo "installing requirements with pip3. . ."
pip3 install -r requirements.txt || { echo "failed to install pip packages, aborting. . ."; exit 1; }

### use systemd to run playerCountBot on system startup
echo "Setting up playerCountBot.py to run on system startup"
# make a unit file for this systemd service
echo "creating unit file 'playerCountBot.service'"
    cat > playerCountBot.service <<UNITFILE
[Unit]
Description=Runs playerCountBot.py script on startup
Wants=network-online.target
After=network-online.target
[Service]
User=$(whoami)
Group=$(id -gn)
ExecStart=/usr/bin/python3 "$PWD/playerCountBot.py"
[Install]
WantedBy=multi-user.target
UNITFILE
# put the unitfile in its place w/ systemd
sudo mv playerCountBot.service /etc/systemd/system/playerCountBot.service
# reload systemd so it can find this newly created service
echo "reloding systemctl daemon"
sudo systemctl daemon-reload
# enable this service in systemd
echo "enabling playerCountBot.service"
sudo systemctl enable playerCountBot.service

echo "playerCountBot service has been added and enabled"
echo "playerCountBot.py will be automatically run on startup from now on"
echo ""
echo "to dissable running on startup type 'sudo systemctl disable playerCountBot.service'"
echo ""

exit 0