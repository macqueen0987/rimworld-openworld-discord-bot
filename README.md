# Rimworld-Openworld-Discord-Bot
This is a Discord.py bot that helps taking care of rimworld openworld mod server.
I'll try to add more features in the future


## Open World Mods page

https://steamcommunity.com/sharedfiles/filedetails/?id=2768146099

## Open World mod server file github

https://github.com/TastyLollipop/OpenWorld


This has nothing to do with the openworld mod developer, I am making for my own use.

## List of commands - most of it's commands are same with server console
Helps are written as thinking the prefix is ! as default    
[] <- these are places for parameters in it. Ex) !s [server commands] -> !s help
```
!hi        : answers back to you
!ping      : show ping
!uptime    : show how long the bot has been running

---Under this line requires discord server moderator commands---
!shutdown                         : shutdowns this bot
!s [some command]                 : sends command to screen which openworld server is running
!reload                           : reloads mods and whitelists   
!status                           : get server status   
!start                            : starts the openworld server
!exit                             : shutdowns the openworld server
!console [some command]           : sends command directly to server file directory   
!download [mod id]                : dowloads mod using steamcmd. add "required" in between to download it at Mods folder
!delete [mod id]                  : deletes mod
!say [something to say]           : sends message in chat   
!notify [user] [something to say] : notifies user   
!broadcast [something to say]     : broadcast message   
!whitelist [user id]              : toggles user in whitelist
!auto_update                      : toggles auto_update mod. WARNING: updating mods are very slow and all mods will be deleted when updating
```

## Setup
Run the setup.py and you will get all the pip libraries.   
In case it fails the required are discord.py, importlib, asyncio, requests, beautifulsoup4    
I am currently using python 3.8.10 which is here https://www.python.org/downloads/release/python-3810/

### Setting up discord bot
https://discordpy.readthedocs.io/en/stable/discord.html
### Setting up Steamcmd
We will be using Steamcmd to download mods.   
I used manual installation.   
https://developer.valvesoftware.com/wiki/SteamCMD#Manually
### Starting the bot
Fill in the var.py file whith your informations.   
Create a screen where you will run the openworld mod server and enable the logging by pressing ctrl + a, shift h.      
It HAS to be created at the same loaction and as the same name with server_dir, screen_name in var.py      
Then run the bot at another screen.   
