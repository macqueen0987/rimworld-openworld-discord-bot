
# Your discord ID in int
me = 11111

# bot token
token = 'your_bot_token'


#==============================================================SOME LINE FOR ORGANIZATION===================================================

# prefix
prefix = '!'

server_dir = '../rimworld/'     # loaction of rimworld openworld mod server dir
steam_dir = '../Steam/'         # dir where steamcmd.sh is loacted. download mods via steamcmd
screen_name = 'rimworld'        # screen name where you are running Open World Server

logfile = 'screenlog.0'         # logfile of the screen from server_dir. please make screen in server directory.

wait_for_log = 10               # time you will wait for the log, if too short you may not get the logs from inputs

max_line = 40                   # max line for bot output becaus discord has max amount of letters you can send
mention_author = False          # metion author in message, if True it will always mention you. i perfer off

auto_update_mods = 24           # invterval to auto update the mods in hours. updating mods are slow and deletes all mods in folder when started.
                                # Couldn't think of a better way of updating mods...
auto_update = False             # toggle auto update of mods. if True, it will start updating mods in the start of bot

use_dlc = True                  # whether to use dlc as whitelist mods
#====================================================SPACE FOR MODS=============================================
# neccessary mods steam collection id, set None if it doesn't exist
# id can be found in mods collection page url, after the filedetails/?id=
mods = None

# whitelist mods steam collection id, set None if it doesn't exist
# id can be found in mods collection page url, after the filedetails/?id=
whitelist_mods = None
