from __future__ import unicode_literals
import os
import discord
import time
from random import randint
from discord.ext import tasks
import importlib
import asyncio
import requests
import subprocess
import shutil
import sys
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import traceback
import platform

import var
import server
import rimworld

restart = False


def main():
    var.init()

    def reload():
        importlib.reload(var)
        importlib.reload(server)
        importlib.reload(rimworld)
        pass


    async def start_server():
        var.console_out = ''
        t = Thread(target=server.run)
        t.daemon = True
        t.start()
        await asyncio.sleep(2)


    start = 0
    client = discord.Client()
    # reload()

    def convert(time):

        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        temp = ''
        if day != 0: temp += "%d days " % day
        if hour != 0: temp += "%d hours " % hour
        if minutes != 0: temp += "%d minutes " % minutes
        if seconds != 0: temp += "%d seconds" % seconds
        return temp


    @client.event
    async def on_message(message):
        global restart

        async def send_to_server(msg):
            var.console_out = ''
            await asyncio.gather(server.write_stdin(var.server_proc.stdin, msg))
            await asyncio.sleep(var.wait_for_log)

        mention_author = var.mention_author
        if not mention_author:
            allowed_mentions = discord.AllowedMentions.none()
        # we do not want the bot to reply to itself
        if message.author == client.user or message.author.bot is True:
            return

        if message.guild is None:  # forbid DM to bot 
            return


    
        color = randint(0, 0xFFFFFF)


        if message.content.startswith(var.prefix):
            msg = message.content.split(' ')[0].replace(var.prefix,"").lower()
                    

            if msg.startswith('hi'):
                msg = 'hi {0.author.mention}'.format(message)
                await message.reply(msg, mention_author=mention_author)
                


            if msg.startswith('ping'):
                time_then = time.monotonic()
                pinger = await message.reply('__*`Pinging...`*__', mention_author=mention_author)
                ping = '%.2f' % (1000*(time.monotonic()-time_then))
                # allowed_mentions = discord.AllowedMentions.none()
                await pinger.edit(content = ':ping_pong: \n **Pong!** __**`' + ping + 'ms`**__', allowed_mentions=allowed_mentions)
                

            if msg in ['shutdown', 'restart']:
                restart = False
                if message.author.id == var.me:
                    if msg == 'shutdown':
                        msg = "shutting down..."

                    if msg == "restart":
                        if var.python is None:
                            msg = "Can't restart automatically... Please try it Manually!"
                            await message.reply(msg.format(message), mention_author=mention_author)
                            return
                        else:
                            msg = "Restarting bot..."
                            restart = True


                    if var.server_proc is not None:
                        message = await message.reply("Stopping Server...", mention_author=mention_author)
                        await send_to_server("exit")
                        await message.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                    else:
                        message = await message.reply(msg.format(message), mention_author=mention_author)

                    client.clear()
                    await client.close()
                    if restart and var.python is not None:
                        print("\n\n==================")
                        print("restarting the bot")
                        print("==================\n\n")
                        open(f"channel_{message.channel.id}", 'a').close()
                        open(f"message_{message.id}", 'a').close()
                        if var.Windows: os.system("./"+sys.argv[0])
                        else: os.system(var.python + " " + sys.argv[0])

                else:
                    msg = ["Only my master can do it", "Heroes nver die", "That's a no no","shutting down...\n||No way i will||"]
                    msg = "{0.author.mention}"+msg[randint(0,len(msg)-1)]
                    await message.reply(msg.format(message), mention_author=mention_author)
                    


            if msg == 'uptime':
                msg = 'uptime: ' + convert(time.time() - start)
                await message.reply(msg.format(message), mention_author=mention_author)
                


             # =============under this line requires administrator rights=================
            if not message.author.guild_permissions.administrator: 
                if message.author.id == var.me:
                    pass
                else:
                    return

            #----------------------------Some things that Don't require server-----------------
            # command that is going to normal console to do simple things
            if msg == 'c':  
                params = message.content.replace(var.prefix + "c ", "")
                temp = await message.reply("sending the command..".format(message), mention_author=mention_author)
                log = await rimworld.raw_console_command(params)

                msg = log[0] + "\n```\n" + log[1] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                if len(log) > 2:
                    for i in range(2,len(log)):
                        await temp.channel.send("```\n"+ log[i] + "```".format(message), mention_author=mention_author)

                

            # download the mod; include "required" to make it must have mod
            if msg == 'download':  
                params = message.content.replace(var.prefix + "download ", "")
                required = False
                if "required" in params:
                    params = params.replace("required ","")
                    required = True
                temp = await message.reply("Starting the download".format(message), mention_author=mention_author)
                log = await rimworld.download_mod(params, required)

                msg = "Command ended. With following logs:\n```\n" + log + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)
                

            # deletes mod
            if msg == 'delete':  
                params = message.content.replace(var.prefix + "delete ", "")
                msg = rimworld.delete_mod(params)
                await message.reply(msg.format(message), mention_author=mention_author)
                

            # toggle user into whitelist
            if msg == 'whitelist':  
                if len(message.content.split(" ")) < 2:
                    whitelist = var.server_dir + '"Whitelisted Players.txt"'
                    process = os.popen('cat ' + whitelist)
                    preprocessed = process.read()
                    process.close()
                    msg = "Whitelisted players\n```\n" + preprocessed + "``` Can be different from server." 
                    await message.reply(msg.format(message), mention_author=mention_author)
                    return
                params = message.content.replace(var.prefix + "whitelist ", "")
                msg = rimworld.whitelist(params)
                msg = "Successfully modified. Current whitelist:\n```\n" + msg + "```Reload the server to apply changes!"
                await message.reply(msg.format(message), mention_author=mention_author)
                

            # update mods manually
            if msg == "update_mods":
                log = False
                noreload = False
                quick = False

                argv = message.content.replace(var.prefix+"update_mods", "").replace(" ","")
                if "-" in argv:
                    argv = argv.replace("-",'')
                    if "log" in argv: log = True; argv = argv.replace("log","")
                    if "noreload" in argv: noreload = True; argv = argv.replace("noreload","")
                    if 'quick' in argv: quick = True; argv = argv.replace("quick","")

                    if len(argv) != 0:
                        await message.reply("Unknown parameter : %s" % (argv), mention_author=mention_author)
                        return
                
                else:
                    if len(argv) != 0:
                        await message.reply("Unknown parameter : %s" % (argv), mention_author=mention_author)
                        return

                msg = "Starting update"
                temp = await message.reply(msg.format(message), mention_author=mention_author)
                if var.auto_update:
                    update_mods.cancel()
                    log = await rimworld.update_mods(client, message=temp, log=log, noreload=noreload, quick=quick)
                else:
                    await rimworld.update_mods(client, message=temp, log=log, noreload=noreload, quick=quick)

                msg = "updated mods"
                await client.change_presence(activity=discord.Game(name="Mod Auto Update OFF"))
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)
                await update_mods.start()
                

            # only download the dlcs
            if msg == "add_dlc":
                rimworld.add_dlc()
                msg = "Added DLC"
                await message.reply(msg.format(message), mention_author=mention_author)
                

            # toggle auto update.
            if msg == "auto_update":
                if var.auto_update:
                    update_mods.cancel()
                    msg = 'stopped'
                else:
                    update_mods.start()
                    msg = 'running'
                var.auto_update = not var.auto_update
                msg = "Successfully modified. Auto update is currently " + msg
                await message.reply(msg.format(message), mention_author=mention_author)
            

            # start the server
            if msg == 'start':
                if var.server_proc is not None:
                    message = await message.reply('Server is already runnning.', mention_author=mention_author)
                    await send_to_server('status')
                    await message.edit(content = message.content + f'\n```\n{var.console_out}```', allowed_mentions=allowed_mentions)
                else:
                    message = await message.reply('Starting Server', mention_author=mention_author)
                    await start_server()
                    await message.edit(content = f'Started Server\n```\n{var.console_out}```'.format(message), allowed_mentions=allowed_mentions)
                

            # get server status
            if msg == 'status':
                if var.server_proc is None:
                    await message.reply(f'Server is Offline', mention_author=mention_author)
                else:
                    message = await message.reply('Server is Online', mention_author=mention_author)
                    await send_to_server("status")
                    await message.edit(content = message.content+f'\n```\n{var.console_out}```', allowed_mentions=allowed_mentions)
                

            # shut down server
            if msg == 'exit':
                if var.server_proc is None:
                    await message.reply(f"server is Offline currently. \nUse {var.prefix}start to start the server".format(message), mention_author=mention_author)
                else:
                    message = await message.reply('Shutted down server', mention_author=mention_author)
                    await send_to_server("exit")
                

            # reload bot with configurations
            if msg == "reload_bot":
                var.init()
                reload()
                msg = 'Reloaded bot configurations. \nYou might have to restart the bot for some features to take effect'
                message = await message.reply(msg.format(message), mention_author=mention_author)
                

            # reload bot with configurations
            if msg == "reload_bot":
                var.init()
                reload()
                msg = 'Reloaded bot configurations. \nYou might have to restart the bot for some features to take effect'
                message = await message.reply(msg.format(message), mention_author=mention_author)


            if msg == 'log':
                temp = await message.reply("Fetching logs...", mention_author = mention_author)
                logs = var.console_out
                if logs.replace('\n','').replace(' ','') == '':
                    await message.edit('No logs to display', allowed_mentions=allowed_mentions)
                    return
                logs = logs.split('\n')
                cnt = 0
                msg = []
                if len(logs) < var.max_line:
                    msg.append(var.console_out)
                else:
                    cnt = 0
                    msg = []
                    temp = ''
                    for i in logs:
                        if cnt == var.max_line:
                            msg.append(temp)
                            temp = ''
                            cnt = 0
                        temp += i + '\n'
                        cnt += 1
                    msg.append(temp)

                log = msg

                msg = "Logs:\n```\n" + log[0] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                if len(log) > 1:
                    for i in range(1,len(log)):
                        await temp.channel.send("```\n"+ log[i] + "```".format(message), mention_author=mention_author)


        # ------------------------------------Things that have to do with Servers-----------------------
        if message.content.startswith(var.server_prefix):
            if not message.author.guild_permissions.administrator: 
                if message.author.id == var.me:
                    pass
                else:
                    return

            if var.server_proc is None:
                await message.reply("You need to start the Server First!", mention_author=mention_author)
                return

            # send message to server : <server_prefix><somthing to send>
            msg = message.content[1:]
            while msg[0] == ' ': msg = msg[1:]
            message = await message.reply(f'Sending "{msg}" to server', mention_author=mention_author)
            await send_to_server(msg)
            logs = var.console_out.split("\n")
            cnt = 0
            log_arr = []
            temp = ''
            for log in logs:
                if cnt >= var.max_line:
                    log_arr.append(temp)
                    temp = ''
                    cnt = 0
                temp += log + '\n'
                cnt += 1
            log_arr.append(temp)
            await message.edit(content = f'"{msg}" sent to server\n```\n{log_arr[0]}```'.format(message), allowed_mentions=allowed_mentions)
            if len(log_arr) > 1:
                for i in range(1,len(log_arr)):
                    await message.channel.send("```\n"+ log_arr[i] + "```".format(message), mention_author=mention_author)
        


    @tasks.loop(hours=1)
    async def update_mods():
        hours = (time.time() - start_update) // 3600
        if hours >= var.auto_update_mods:
            await client.change_presence(activity=discord.Game(name="Updating Mods"))
            await rimworld.update_mods(client)

        await client.change_presence(activity=discord.Game(name="Next update: "+str(int(24 - hours))+"hours"))


    @client.event
    async def on_ready():
        print("=================\n==launching bot==\n=================")
        global start
        global restart
        await start_server()

        if restart:
            message = await client.get_channel(restart_channelid).fetch_message(restart_messageid)
            await message.edit(content = "Restarted!", allowed_mentions=discord.AllowedMentions.none())
            restart = False

        if var.auto_update:
            update_mods.start()
        else:
            await client.change_presence(activity=discord.Game(name="Mod Auto Update OFF"))


    start = time.time()
    start_update = time.time()
    try:
        client.run(var.token)
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info
        input("Press enter to continue...")
        exit()



def versiontuple(v):
    return tuple(map(int, (v.split("."))))



if __name__ == '__main__':
    # global restart, restart_messageid, restart_channelid
    files = os.listdir(".")
    if "var.json" not in files:
        print("==Cannot find var.json!==")
        input("Press enter to continue...")
        exit()


    if platform.system() == "Windows":
        print("Currently, all i can do for windows is to update mods due to mismatch with things.")
        print("see var.json for how to")
        input("Press enter to close")
        exit()


    var.server_dir = os.getcwd() + '/'

    if "Open World Server" not in str(files):
        print("==Must be placed with the server file!==")
        input("Press enter to continue...")
        exit()


    for file in files:
        if file.startswith("message_"):
            restart = True
            restart_messageid = int(file.replace("message_",""))
            os.remove(file)
        if file.startswith("channel_"):
            restart_channelid = int(file.replace("channel_",""))
            os.remove(file)


    if sys.argv[0].endswith(".py"):
        version = sys.version.split(' ')[0]
        if version.startswith("2"):
            print("No python 2")
            exit()

        if versiontuple(version) != versiontuple("3.8.10"):
            print("\n\n==WARNING! python version mismatch. You may experience some bugs. Recommended to use version 3.8.10. Continuing... ==")
        else:
            print("\n\n==Checked python 3.8.10==")

        found_python = os.popen('python --version').read()

        if "not found" not in found_python and len(found_python.replace('\n',"").replace(' ',"")) > 0:
            if versiontuple(version) == versiontuple(found_python.split(" ")[1]):
                var.python = "python"
                print("\n\n==Found python path. Will be able to restart bot by discord==")

        else:
            found_python = os.popen('python3 --version').read()
            if "not found" not in found_python and len(found_python.replace('\n',"").replace(' ',""))> 0:
                if versiontuple(version) == versiontuple(found_python.split(" ")[1]):
                    var.python = "python3"
                    print("\n\n==Found python path. Will be able to restart bot by discord==")
            else:
                var.python = None
                print("\n\n==where.... is.... python? You will have to Manually restart the bot.==")

    var.Windows = False
    if sys.argv[0].endswith(".exe"):
        print("Hello Windows!")
        var.Windows = True

    main()
