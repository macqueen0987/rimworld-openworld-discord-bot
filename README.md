# Rimworld-Openworld-Discord-Bot
Warning: bot and server doesn't work on Windows, all it does is updating mods      
This is a auto server mod update program and a Discord.py bot that helps taking care of rimworld openworld mod server.     
        
I'll try to add more features in the future    
and my english is terrible so are my codes.... but it works anyway
## What can it do?
* update mods in mod collection
* send command to openworld server console
* send command to server directory
* start, stop server
* pretty much discord becomes a cosole for server

## Open World Mods page

https://steamcommunity.com/sharedfiles/filedetails/?id=2768146099

## Open World mod server file github

https://github.com/TastyLollipop/OpenWorld        
This has nothing to do with the openworld mod developer, I am making for my own use.

## List of commands - most of it's commands are same with server console
To send commands to server console, check in var.json file for server_prefix.
If you just type something after it, it will be sent to console.
Default value is "/", which stands that /reload will reload the server.

Helps are written as thinking the prefix is ! as default    
[] <- these are places for parameters in it. Ex) !s [server commands] -> !s help
```
!hi        : answers back to you
!ping      : show ping
!uptime    : show how long the bot has been running

---Under this line requires discord server moderator rights---
!start                 : starts the openworld server
!exit                  : shutdowns the openworld server
!shutdown              : shutdowns this bot and server
!reload                : reloads mods and whitelists   
!status                : get server status   
!c [some command]      : sends command directly to server file directory   
!download [mod id]     : dowloads mod using steamcmd. add "required" in between to download it at Mods folder
!delete [mod id]       : deletes mod
!whitelist [user id]   : toggles user in whitelist, only !whitelist will return 'whitelist player.txt'
!update_mods           : manually update mods now
                         : available arguments :  
                            "-log" (prints out everything), 
                            "-noreload" (doesn't reload after update),  
                            "-quick" (faster but doesn't check if files are wrong)
!add_dlc               : add dlc and core as whitelist mods
!auto_update           : toggles auto_update mod.
!reload_bot            : reloads the bot with var.json configurations
!log                   : prints the log of server after your last command                 
```

## Setup
For windows, due to mismatch of things between my program and openworld server program, all it can do is updating mods.      
I think it will not be fixed unless I tell the mod maker about my errors and I am not going to because it's out of priority.      
### Prep things
I am currently using python 3.8.10 which is here https://www.python.org/downloads/release/python-3810/          
Run the setup.py and you will get all the pip libraries if it does it's job.        
In case it fails the required are discord.py, importlib, asyncio, requests, beautifulsoup4     

### Setting up discord bot
https://discordpy.readthedocs.io/en/stable/discord.html     
When inviting the bot, just give it administrator rights because it is going to be your bot anyway...

### Setting up Steamcmd
We will be using Steamcmd to download mods.   
I used manual installation and you need to write steamcmd directory in var.json.    
https://developer.valvesoftware.com/wiki/SteamCMD#Manually    

### Starting the bot
Place the files in the same directory with Open World Server.    
Fill in the var.json file whith your informations.    
Then run the bot. It will automatically start the server with it.     

### Auto mod update without running bot
If you don't want a bot, just fill in parts below the line common thingys in var.json
After you have filled in var.json, running the server.py in the console will update all the mods.      
For windows users, you can't get a autoupdate, and even though you do, it is pointless because i can't send anything to server console due to mismatch of things. 
Which means even though the mods are updated, it won't be reloaded. But running server.py or server.exe will update your mods...                  
For linux users, you can run server.py and it will start your server as well as auto updating mods as in var.json file.

# Currently Working On
* role for server admins (it is currently just server admin and can't change)
