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
from bs4 import BeautifulSoup

import var
import rimworld

conn = None
cur = None



def main():
    def reload():
        importlib.reload(var)
        importlib.reload(rimworld)
        pass

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
            msg = message.content.split(' ')[0].replace(var.prefix,"")
                    

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
                if message.author.id == var.me:
                    if msg == 'shutdown':
                        msg = "shutting down..."
                        restart = False

                    if msg == 'restart':
                        msg = "restarting..."
                        restart = True

                    var.restart = restart
                    await message.reply(msg.format(message), mention_author=mention_author)
                    client.clear()
                    await client.close()

                else:
                    msg = ["Only my master can do it", "Heroes nver die", "That's a no no","shutting down...\n||No way i will||"]
                    msg = "{0.author.mention}"+msg[randint(0,len(msg)-1)]
                    await message.reply(msg.format(message), mention_author=mention_author)


            if msg == 'uptime':
                msg = 'uptime: ' + convert(time.time() - start)
                await message.reply(msg.format(message), mention_author=mention_author)


             # under this line requires administrator rights
            if not message.author.guild_permissions.administrator: 
                if message.author.id == var.me:
                    pass
                else:
                    return

            # basically just put <prefix>s <some commands> to send commands like : !s help
            if msg == 's':
                msg = message.content.replace(var.prefix+"s ","")
                temp = await message.reply("running command.. takes up to "+ str(var.wait_for_log + 5) +" seconds".format(message), mention_author=mention_author)
                log = await rimworld.send_command(msg, True)
                msg = "Executed successfully\n```\n" + log[0] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                if len(log) > 1:
                    for i in range(1,len(log)):
                        await temp.channel.send("```\n"+ log[i] + "```".format(message), mention_author=mention_author)

            # some communucation commands
            if msg in ['broadcast', 'notify', 'say']:  
                await rimworld.send_command(message.content.replace(var.prefix,""))
                await message.reply("message sent", mention_author=mention_author)

            # shortcut for reload
            if msg == "reload":
                temp = await message.reply("running command.. takes up to "+ str(var.wait_for_log + 5) +" seconds".format(message), mention_author=mention_author)
                log = await rimworld.send_command('reload', True)
                msg = "Reloaded successfully\n```\n" + log[0] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

            # shortcut for shuting down the server
            if msg == "exit":
                temp = await message.reply("running command.. takes up to "+ str(var.wait_for_log + 5) +" seconds".format(message), mention_author=mention_author)
                await rimworld.send_command('exit')
                await temp.edit(content = "Server is now terminated", allowed_mentions=allowed_mentions)

            # shortcut for starting the server
            if msg == "start":
                temp = await message.reply("running command.. takes up to "+ str(var.wait_for_log + 5) +" seconds".format(message), mention_author=mention_author)
                log = await rimworld.send_command('reload', True)
                msg = "Server started with following logs\n```\n" + log[0] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

            # command that is going to server directory to do simple things
            if msg == 'console':  
                params = message.content.replace(var.prefix + "console ", "")
                temp = await message.reply("sending the command..".format(message), mention_author=mention_author)
                log = await rimworld.raw_console_command(params)

                msg = "Command sent successfully\n```\n"+ log[0] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                if len(log) > 1:
                    for i in range(1,len(log)):
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
                params = message.content.replace(var.prefix + "whitelist ", "")
                msg = rimworld.whitelist(params)
                msg = "Successfully modified. Current whitelist:\n```\n" + msg + "```Reload the server to apply changes!"
                await message.reply(msg.format(message), mention_author=mention_author)

            if msg == "auto_update":
                if var.auto_update:
                    update_mods.stop()
                    msg = 'stopped'
                else:
                    update_mods.start()
                    msg = 'running'
                var.auto_update = not var.auto_update
                msg = "Successfully modified. Auto update is currently " + msg
                await message.reply(msg.format(message), mention_author=mention_author)


    @tasks.loop(hours=var.auto_update_mods)
    async def update_mods():
        await client.change_presence(activity=discord.Game(name="Updating Mods"))
        rimworld.update_mods()
        await client.change_presence(activity=discord.Game(name="Listening to Commands"))


    @client.event
    async def on_ready():
        global start
        reload()

        if var.auto_update:
            update_mods.start()
        else:
            await client.change_presence(activity=discord.Game(name="Listening to Commands"))

    start = time.time()
    client.run(var.token)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())