import subprocess
import shutil
import os

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
        folder = 'Whitelisted\ Mods/'
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
        stdout += '\n\ninfo: already existing mod, reinstalling'
    except Exception as e:
        stdout += '\n\ninfo: ' + str(e)


    try:
        download_folder = steam_library + 'steamapps/workshop/content/294100/' + mod_id
        shutil.move(download_folder, steam_library)

        shutil.rmtree(steam_library+'steamapps')
        stdout += '\n\ninfo: All Done!'
    except Exception as e:
        stdout += '\n\nerror:' + str(e)

    return stdout


def delete_mod(mod_id):
    mod_id = str(mod_id)
    folders = ['Mods/', 'Whitelisted\ Mods/']
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


def whiteliste(user):
    pass




async def reload():
    return await send_command("reload", True)


async def broadcast(msg):
    msg = 'broadcast ' + msg
    return await send_command(msg)


async def status():
    return await send_command("status", True)


async def notify(player, msg):
    msg = 'notify %s %s' % (player, msg)
    return await send_command(msg) 

# asyncio.run(raw_console_command("ls -l"))