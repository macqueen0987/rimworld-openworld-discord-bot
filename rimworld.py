import subprocess
import shutil
import os
import requests
from bs4 import BeautifulSoup
import sys

import var
import asyncio

max_line = var.max_line


async def send_command(command, log = False):
    screen_name = var.screen_name
    logfile = var.server_dir + var.logfile
    try:
        os.remove(logfile)
    except Exception as e:
        print(e)

    screen_command = 'screen -L -S %s -p 0 -X stuff "%s\n"' % (screen_name, command)
    os.system(screen_command)

    if log:
        await asyncio.sleep(var.wait_for_log)

        process = os.popen('cat ' + logfile)
        preprocessed = process.read()
        preprocessed = preprocessed.replace("[39;49m","").replace("[37m","").replace("[32m","").replace("[H[J","")
        processed = preprocessed.split('\n')
        if len(processed) < max_line:
            msg = [preprocessed]
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
        process.close()

        return msg


async def raw_console_command(command):

    cwd = os.getcwd()
    os.chdir(var.server_dir)
    process = os.popen(command)
    preprocessed = process.read()
    process.close()
    os.chdir(cwd)

    processed = preprocessed.split('\n')
    if len(processed) < max_line:
        msg = [preprocessed]
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
    steamcmd = var.steam_dir + "steamcmd.sh"
    login = "+login anonymous"
    install_dir = str('+force_install_dir "'+steam_library+'"')
    download_mod = "+workshop_download_item 294100 "+ str(mod_id)
    process = subprocess.Popen([steamcmd, install_dir, login, download_mod, "+quit"], stdout=subprocess.PIPE)
    stdout = process.communicate()[0]
    stdout = stdout.decode('ascii')
    try:
        shutil.rmtree(steam_library + mod_id)
        stdout += '\ninfo: already existing mod, reinstalling'
    except Exception as e:
        stdout += '\ninfo: new mod'


    try:
        download_folder = steam_library + 'steamapps/workshop/content/294100/' + mod_id
        shutil.move(download_folder, steam_library)

        shutil.rmtree(steam_library+'steamapps')
        stdout += '\ninfo: All Done!\n\n'
    except Exception as e:
        stdout += '\nerror:' + str(e) + '\n\n'

    return stdout


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
    whitelist = var.server_dir + 'Whitelisted\ Players.txt'
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


    with open(var.server_dir + 'Whitelisted Players.txt', "w") as file:
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
    cwd = os.getcwd()
    os.chdir(var.server_dir + 'Whitelisted Mods/')
    os.system('wget https://github.com/TastyLollipop/OpenWorld/raw/main/DLCs.zip')
    os.system('unzip DLCs.zip')
    os.system('rm -rf DLCs.zip')
    os.chdir(cwd)
    if not silent: print("Done Adding DLC")

# when you want to just keep the mods updated, only change mods in var.py file
def update_mods(silent = True, autoreload = True):  # change silent to false if you want to see everything and autoreload to False if you don't want to reload
    url = 'https://steamcommunity.com/sharedfiles/filedetails/?id='


    if var.mods is not None:
        mods = get_mods(url + str(var.mods))
        if not silent: print('Updating %d required mods' % len(mods))

        cwd = os.getcwd()
        os.chdir(var.server_dir + 'Mods/')
        process = os.popen('rm -rf *')
        process.close()
        os.chdir(cwd)

        for mod in mods:
            msg = asyncio.run(download_mod(mod, required = True))
            if not silent: print(msg)
        if not silent: print("\n\nAll Done updating required mods\n\n")

    else:
        if not silent: print("\n\nno required mods\n\n")

    if var.whitelist_mods is not None:
        mods = get_mods(url + str(var.whitelist_mods))
        if not silent: print('Updating %d whitelist mods' % len(mods))

        cwd = os.getcwd()
        os.chdir(var.server_dir + 'Whitelisted Mods/')
        process = os.popen('rm -rf *')
        process.close()
        os.chdir(cwd)

        for mod in mods:
            msg = asyncio.run(download_mod(mod, required = False))
            if not silent: print(msg)

        if not silent: print("\n\nAll Done updating whitelist mods\n\n")

    else:
        if not silent: print("\n\nno whitelist mods\n\n")

    if var.use_dlc:
        add_dlc(silent)

    if autoreload:
        if not silent: print("start to reload....")
        msg = asyncio.run(send_command("reload", log = True))
        if not silent: print(msg[0])


if __name__ == '__main__':
    result = update_mods(silent = False, autoreload = True)