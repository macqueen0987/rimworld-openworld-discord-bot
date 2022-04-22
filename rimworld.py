import subprocess
import shutil
import os
import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import unquote
from urllib.request import urlretrieve
import discord
import asyncio
import platform
import zipfile

import var
import server

var.init()
max_line = var.max_line


async def send_to_server(msg):
    await asyncio.gather(server.write_stdin(var.server_proc.stdin, msg))
    await asyncio.sleep(var.wait_for_log)


async def raw_console_command(command):

    if "cd" in command:
        param = command.replace("cd ","")
        os.chdir(param)
        command = "ls"
        
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()


    msg = [f'{command!r} exited with {process.returncode}']
    if stdout:
        preprocessed = stdout.decode()

    if stderr:
        preprocessed = stderr.decode()

    processed = preprocessed.split('\n')

    if len(processed) < max_line:
        msg.append(preprocessed)
    else:
        cnt = 0
        msg = []
        temp = ''
        for i in processed:
            if cnt == max_line:
                msg.append(temp)
                temp = ''
                cnt = 0
            temp += i + '\n'
            cnt += 1
        msg.append(temp)

    return msg


async def download_mod(mod_id, required = False):

    mod_id = str(mod_id)

    if required:
        folder = 'Mods/'
    else:
        folder = 'Whitelisted Mods/'
    steam_library = var.server_dir + folder
    if platform.system() == "Linux": steamcmd = var.steam_dir + "steamcmd.sh "
    if platform.system() == "Windows": steamcmd = var.steam_dir + "steamcmd.exe "
    login = "+login anonymous "
    install_dir = str('+force_install_dir "'+steam_library+'" ')
    download_mod = "+workshop_download_item 294100 "+ str(mod_id)
    process = await asyncio.create_subprocess_shell(steamcmd + login + install_dir + download_mod + " +quit", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    msg = f'exited with {process.returncode}\n\n'
    if stdout:
        msg += stdout.decode()

    if stderr:
        msg += stderr.decode()
    try:
        shutil.rmtree(steam_library + mod_id)
        msg += '\ninfo: already existing mod, reinstalling'
    except Exception as e:
        msg += '\ninfo: new mod'


    try:
        download_folder = steam_library + 'steamapps/workshop/content/294100/' + mod_id
        shutil.move(download_folder, steam_library)

        shutil.rmtree(steam_library+'steamapps')
        msg += '\ninfo: All Done!\n\n'
    except Exception as e:
        msg += '\nerror:' + str(e) + '\n\n'

    return msg


def delete_mod(mod_id):
    mod_id = str(mod_id)
    folders = ['Mods/', 'Whitelisted Mods/']
    deleted = False
    for folder in folders:
        steam_library = var.server_dir + folder
        try:
            shutil.rmtree(steam_library + mod_id)
            deleted = True
        except Exception as e:
            pass

    if deleted:
        return "deleted the mod"
    else:
        return "this mod is not installed"


def whitelist(user):
    whitelist = var.server_dir + '"Whitelisted Players.txt"'
    process = os.popen('cat ' + whitelist)
    preprocessed = process.read()
    process.close()

    found = False
    processed = preprocessed.split('\n')
    for i in range(len(processed)):
        if user == processed[i]:
            found = True
            processed.pop(i)

        if found:
            break

    if not found:
        preprocessed += '\n' + user
    
    else:
        preprocessed = ''
        for i in processed:
            preprocessed += i + '\n'
        preprocessed = preprocessed[:-1]


    with open(var.server_dir + '"Whitelisted Players.txt"', "w") as file:
        file.write(preprocessed)
        file.close()

    return preprocessed


def get_mods(url):
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        # print(html)
        soup = BeautifulSoup(html, 'html.parser')
        soup = soup.find_all("div", class_="collectionItem")
        dic = []
        for i in soup:
            dic.append(i.get("id").replace("sharedfile_",""))

        return dic

    else: 
        print(response.status_code)
        return None


def add_dlc(silent = True):
    if not silent: print("Adding DLC to whitelist mods")
    dlc_link = var.dlc_link
    cwd = os.getcwd()
    os.chdir(var.server_dir + 'Whitelisted Mods/')
    urlretrieve(dlc_link, "DLCs.zip")
    with zipfile.ZipFile("DLCs.zip") as unzip:
        unzip.extractall("./")
    os.remove("DLCs.zip")
    os.chdir(cwd)
    if not silent: print("Done Adding DLC")


async def update_mods(client, message = None, log = False, noreload = False, quick = False): 
    url = 'https://steamcommunity.com/sharedfiles/filedetails/?id='
    allowed_mentions = discord.AllowedMentions.none()
    mention_author = var.mention_author

    msg_, print_= False, False
    if message is not None and not log:
        msg_ = True

    if message is not None and log:
        print_ = True


    if var.mods is not None:
        mods = get_mods(url + str(var.mods))
        if print_: msg = 'Updating %d required mods' % len(mods)
        if print_: message = await message.channel.send(msg.format(message), mention_author=mention_author)

        cwd = os.getcwd()
        os.chdir(var.server_dir)
        lists = os.listdir("Mods/")
        if not quick:
            if os.path.exists("./Mods_backup"):
                shutil.rmtree("./Mods_backup")
            os.mkdir("./Mods_backup")
            for list_ in lists:
                shutil.move("Mods/"+list_, "Mods_backup/")


        if quick:
            need_to_remove = []
            for list_ in lists:
                if list_ == '' or not list_.isnumeric(): pass
                else:
                    if list_ not in mods:
                        need_to_remove.append(list_)

            need_to_download = []
            for mod in mods:
                if mod not in lists:
                    need_to_download.append(mod)

            mods = need_to_download

            if len(need_to_remove) > 0:
                await message.edit(content = f'Deleting {len(need_to_remove)} required mods that are unnecessary', allowed_mentions=allowed_mentions)
                for mod in need_to_remove:
                    shutil.rmtree(f"Mods/{mod}")
            else:
                await message.edit(content = 'No required mods that are unnecessary', allowed_mentions=allowed_mentions)
            await asyncio.sleep(1)

        os.chdir(cwd)

        cnt = 0

        if len(mods) > 0:
            for mod in mods:  # required mods
                cnt += 1

                msg = "Mod Update %d/%d" % (cnt, len(mods))
                await client.change_presence(activity=discord.Game(name=msg))

                msg = "Updating required mods: %d of %d" % (cnt, len(mods))
                if msg_: await message.edit(content = msg.format(message), allowed_mentions=allowed_mentions)
                if print_: message = await message.channel.send(msg.format(message), mention_author=mention_author)

                msg += '```\n' + await download_mod(mod, required = True) + '```'
                if print_: await message.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

        if not quick:
            cwd = os.getcwd()
            os.chdir(var.server_dir)
            shutil.rmtree("Mods_backup")
            os.chdir(cwd)

        if print_: message = await message.channel.send("All done updating required mods", mention_author=mention_author)


    else:
        if msg_: await message.edit(content = "no required mods", allowed_mentions=allowed_mentions)
        if print_: message = await message.channel.send("no required mods", mention_author=mention_author)

    await asyncio.sleep(1)

    if var.whitelist_mods is not None:
        mods = get_mods(url + str(var.whitelist_mods))
        if print_: msg = 'Updating %d whitelist mods' % len(mods)
        if print_: message = await message.channel.send(msg.format(message), mention_author=mention_author)

        cwd = os.getcwd()
        os.chdir(var.server_dir)
        lists = os.listdir("Whitelisted Mods/")
        if not quick:
            if os.path.exists("./whitelist_Mods_backup"):
                shutil.rmtree("./whitelist_Mods_backup")
            os.mkdir("./whitelist_Mods_backup")
            for list_ in lists:
                shutil.move("Whitelisted Mods/"+list_, "whitelist_Mods_backup/")


        if quick:
            need_to_remove = []
            for list_ in lists:
                if list_ == '' or not list_.isnumeric(): pass
                else:
                    if list_ not in mods:
                        need_to_remove.append(list_)

            need_to_download = []
            for mod in mods:
                if mod not in lists:
                    need_to_download.append(mod)

            mods = need_to_download

            if len(need_to_remove) > 0:
                await message.edit(content = f'Deleting {len(need_to_remove)} whitelist mods that are unnecessary', allowed_mentions=allowed_mentions)
                for mod in need_to_remove:
                    shutil.rmtree(f"Whitelisted Mods/{mod}")

            else:
                await message.edit(content = 'No whitelist mods that are unnecessary', allowed_mentions=allowed_mentions)    
            await asyncio.sleep(1)

        os.chdir(cwd)

        cnt = 0
        if len(mods) > 0:
            for mod in mods:
                cnt += 1

                msg = "Mod Update %d/%d" % (cnt, len(mods))
                await client.change_presence(activity=discord.Game(name=msg))

                msg = "Updating whitelist mods: %d of %d" % (cnt, len(mods))
                if msg_: await message.edit(content = msg.format(message), allowed_mentions=allowed_mentions)
                if print_: message = await message.channel.send(msg.format(message), mention_author=mention_author)

                msg += '```\n' + await download_mod(mod, required = False) + '```'
                if print_: await message.edit(content = msg.format(message), allowed_mentions=allowed_mentions)

        if not quick:
            cwd = os.getcwd()
            os.chdir(var.server_dir)
            shutil.rmtree("whitelist_Mods_backup")
            os.chdir(cwd)

        if print_: message = await message.channel.send("All done updating Whitelisted mods", mention_author=mention_author)

    else:
        if msg_: await message.edit(content = "no whitelist mods", allowed_mentions=allowed_mentions)
        if print_: message = await message.channel.send("no whitelist mods", mention_author=mention_author)

    await asyncio.sleep(1)

    if var.use_dlc and not quick:
        add_dlc()

    if not noreload and var.server_proc is not None:
        if print_: message = await message.channel.send("start to reload....".format(message), mention_author=mention_author)
        msg = "Reloaded!"
        await send_to_server("reload")
        if log: msg += "\n```\n" + var.console_out + '```'
        if print_: await message.edit(content=msg.format(message), allowed_mentions=allowed_mentions)

    return True
