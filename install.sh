#!/bin/sh

# check for root (user id of 0)
 [ `id -u` -eq 0 ] && echo "this script should not be run as root" && exit 1

# get discord token from user
echo "get the bot's token from the discord dev portal and enter it here: "
read DISCORDTOKEN 

# make a config file for inportant variables
echo "creating config file 'config.py'"
    cat > config.py <<CONFIGFILE
class Settings():
    PREFIX = "%"
    DISCORD_TOKEN = "$DISCORDTOKEN"
    BOT_DIR = "$PWD/"
    class Messages():
        # time in seconds for what interval to refresh server info
        REFRESH_TIME = 60 
    class Categories():
        REFRESH_TIME = 300
    class Topics():
        REFRESH_TIME = 300
    class Status():
        REFRESH_TIME = 60
        # if supplied, the address to be tracked for the bot's status
        SERVER_ADDRESS = None
CONFIGFILE
# change permisssions of config file so that other users may not read it
chmod 660 config.py

### install requirements
echo "installing pip with apt. . ."
sudo apt update && sudo apt install python3-pip python3.8-venv -y || { echo "failed to install pip and venv, aborting. . ."; exit 1; }

# make a new venv for the bot
python3.8 -m venv bot_venv

# install python packages within the venv
echo "installing requirements with pip3. . ."
./bot_venv/bin/python3 -m pip install -r requirements.txt || { echo "failed to install pip packages, aborting. . ."; exit 1; }

### use systemd to run playerCountBot on system startup
echo "Setting up playerCountBot to run on system startup"
# make a unit file for this systemd service
echo "creating unit file 'playerCountBot.service'"
    cat > playerCountBot.service <<UNITFILE
[Unit]
Description=Runs playerCountBot script on startup
Wants=network-online.target
After=network-online.target
[Service]
User=$(whoami)
Group=$(id -gn)
WorkingDirectory="$PWD"
ExecStart="$PWD/bot_venv/bin/python3" "$PWD/main.py"
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
echo "playerCountBot will be automatically run on startup from now on"
echo ""
echo "to dissable running on startup type 'sudo systemctl disable playerCountBot.service'"
echo ""

exit 0