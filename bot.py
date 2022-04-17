from __future__ import unicode_literals
import discord
import time
from random import randint
from discord.ext import tasks
import importlib
import os
import asyncio
from pprint import pprint
import requests
from json import loads
import json
import subprocess

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


            if not message.author.guild_permissions.administrator:  # under this line requires administrator rights
                if message.author.id == var.me:
                    pass
                else:
                    return


            if msg == 'reload':
                temp = await message.reply("reloading.. takes up to "+ str(var.wait_for_log + 5) +" seconds".format(message), mention_author=mention_author)
                log = await rimworld.reload()
                msg = "Reloaded successfully\n```" + log[0] + "```"
                await temp.edit(content = msg.format(message), mention_author=mention_author)

                if len(log) > 1:
                    for i in range(1,len(log)):
                        await temp.channel.send("```" + log[i] + "```".format(message), mention_author=mention_author)

            if msg == 'status':
                temp = await message.reply("checking status.. takes up to "+ str(var.wait_for_log + 5) +" seconds".format(message), mention_author=mention_author)
                log = await rimworld.status()
                msg = "Status checked successfully\n```" + log[0] + "```"
                allowed_mentions = discord.AllowedMentions.none()
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                if len(log) > 1:
                    for i in range(1,len(log)):
                        await temp.channel.send("```" + log[i] + "```".format(message), mention_author=mention_author)


            if msg == 'command':
                params = message.content.replace(var.prefix + "command ", "")
                temp = await message.reply("sending the command.. takes up to "+ str(var.wait_for_log + 5) +" seconds".format(message), mention_author=mention_author)
                log = await rimworld.send_command(params, True)

                msg = "Command sent successfully\n```" + log[0] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                if len(log) > 1:
                    for i in range(1,len(log)):
                        await temp.channel.send("```" + log[i] + "```".format(message), mention_author=mention_author)

            if msg == 'console':
                params = message.content.replace(var.prefix + "console ", "")
                temp = await message.reply("sending the command..".format(message), mention_author=mention_author)
                log = await rimworld.raw_console_command(params)

                msg = "Command sent successfully\n```" + log[0] + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

                if len(log) > 1:
                    for i in range(1,len(log)):
                        await temp.channel.send("```" + log[i] + "```".format(message), mention_author=mention_author)

            if msg == 'download':
                params = message.content.replace(var.prefix + "download ", "")
                required = False
                if "required" in params:
                    params = params.replace("required ","")
                    required = True
                temp = await message.reply("Starting the download".format(message), mention_author=mention_author)
                log = await rimworld.download_mod(params, required)

                msg = "Command ended. With following logs:\n```" + log + "```"
                await temp.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

            if msg == 'delete':
                params = message.content.replace(var.prefix + "delete ", "")
                msg = rimworld.delete_mod(params)
                await message.reply(msg.format(message), mention_author=mention_author)

            if msg == 'broadcast':
                params = message.content.replace(var.prefix + "broadcast ", "")
                await rimworld.broadcast(params)
                await message.reply("message broadcasted", mention_author=mention_author)

            if msg == 'notify':
                params = message.content.replace(var.prefix + "notify ", "")
                user = params.split(" ")[0]
                param = params.replace(user + " ","")
                await rimworld.broadcast(user, param)
                await message.reply("notification sent", mention_author=mention_author)





    @client.event
    async def on_ready():
        global start
        reload()


    start = time.time()
    client.run(var.token)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())