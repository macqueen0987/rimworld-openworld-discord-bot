import asyncio
from threading import Thread
import os
import time
import platform
import shutil
import sys
import traceback
import chardet

import var
import rimworld

var.server_proc = None
var.console_out = ''
print_ = False
start = time.time()
encoding = None

async def read_stdout(stdout):
    while True:
        buf = await stdout.readline()
        if not buf:
            break

        global encoding
        encoding = (chardet.detect(buf))['encoding']
        buf = buf.decode(encoding)


        if print_: print(buf, end="")
        var.console_out += buf


async def read_stderr(stderr):
    while True:
        buf = await stderr.readline()
        if not buf:
            break

        encoding = (chardet.detect(buf))['encoding']
        buf = buf.decode(encoding)

        print(buf, end="")


async def write_stdin(stdin, msg):
    var.console_out = ''
    # print(msg)

    try:
        msg = msg+'\n'
        buf = msg.encode(encoding)
        stdin.write(buf)
        await stdin.drain()
        await asyncio.sleep(0.5)
    except:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info


async def update_mods(log = False, noreload = False, quick = False): 
    url = 'https://steamcommunity.com/sharedfiles/filedetails/?id='

    print_ = False
    if log: print_ = True

    if var.mods is not None:
        mods = rimworld.get_mods(url + str(var.mods))
        msg = 'Updating %d required mods' % len(mods)
        print(msg)

        cwd = os.getcwd()
        os.chdir(var.server_dir)
        lists = os.listdir("Mods/")
        if not quick:
            if os.path.exists("Mods_backup"):
                shutil.rmtree("Mods_backup")
            os.mkdir("Mods_backup")

            for list_ in lists:
                shutil.move(f"Mods/{list_}", "Mods_backup/")


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
                print(f'Deleting {len(need_to_remove)} required mods that are unnecessary')
                for mod in need_to_remove:
                    shutil.rmtree(f"Mods/{mod}")
            else:
                print('No required mods that are unnecessary')

        os.chdir(cwd)

        cnt = 0

        if len(mods) > 0:
            for mod in mods:  # required mods
                cnt += 1

                msg = "Updating required mods: %d of %d" % (cnt, len(mods))
                print(msg)

                msg = await rimworld.download_mod(mod, required = True)
                if print_: print(msg)

        if not quick:
            cwd = os.getcwd()
            os.chdir(var.server_dir)
            shutil.rmtree("Mods_backup")
            os.chdir(cwd)

        print("All done updating required mods")


    else:
        print("No required mods")


    if var.whitelist_mods is not None:
        mods = rimworld.get_mods(url + str(var.whitelist_mods))
        msg = 'Updating %d whitelist mods' % len(mods)
        print(msg)

        cwd = os.getcwd()
        os.chdir(var.server_dir)
        lists = os.listdir('Whitelisted Mods/')
        if not quick:
            if os.path.exists("whitelist_Mods_backup"):
                shutil.rmtree("whitelist_Mods_backup")
            os.mkdir("whitelist_Mods_backup")

            for list_ in lists:
                shutil.move(f"Whitelisted Mods/{list_}", "whitelist_Mods_backup/")


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
                print(f'Deleting {len(need_to_remove)} whitelist mods that are unnecessary')
                for mod in need_to_remove:
                    shutil.rmtree(f"Whitelisted Mods/{mod}")

            else:
                print('No whitelist mods that are unnecessary')   


        os.chdir(cwd)

        cnt = 0

        if len(mods) > 0:
            for mod in mods:
                cnt += 1

                msg = "Updating whitelist mods: %d of %d" % (cnt, len(mods))
                print(msg)

                msg = await rimworld.download_mod(mod, required = False)
                if print_: print(msg)

        if not quick:
            cwd = os.getcwd()
            os.chdir(var.server_dir)
            shutil.rmtree("whitelist_Mods_backup")
            os.chdir(cwd)

        print("All done updating Whitelisted mods")

    else:
        print("no whitelist mods")


    if var.use_dlc and not quick:
        rimworld.add_dlc(silent = False)

    if not noreload and var.server_proc is not None:
        print("start to reload....")
        await asyncio.gather(write_stdin(var.server_proc.stdin, "reload"))
        print(var.console_out)


def run():
    loop1 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop1)

    async def async_run():
        # global server_proc
        if platform.system() == "Linux": msg = './Open World Server'
        if platform.system() == "Windows": msg = 'Open World Server.exe'
        print("starting server")
        var.server_proc = await asyncio.create_subprocess_shell(
            msg,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE, shell=True)


        await asyncio.gather(
            read_stderr(var.server_proc.stderr),
            read_stdout(var.server_proc.stdout))


    loop1.run_until_complete(async_run())

    print("Server stopped")
    var.server_proc = None


def update_task():
    global start
    loop2 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop2)

    async def async_update_task():
        global start
        while var.auto_update:
            if (time.time() - start) // 3600 >= var.auto_update_mods:
                update_mods()
                start = time.time()
            await asyncio.sleep(5)
            if not var.auto_update:
                break
        print("===============\nTask is Closed\n===============")

    loop2.run_until_complete(async_update_task())



async def main():
    var.server_dir = os.getcwd() + '/'
    print(var.server_dir)
    global start
    start = time.time()
    global server_proc

    if var.auto_update:
        print("updating mods")
        await update_mods()
        print("Done updating")
        if platform.system() != "Windows":
            update = Thread(target=update_task)
            update.daemon = True
            update.start()
        else:
            print("all_done updating mods")

    if platform.system() != "Windows":
        server = Thread(target=run)
        server.daemon = True
        server.start()

        # client = discord.Client()
        await asyncio.sleep(2)


        def help():
            print("commands:")
            print("/ [say something to server] : say something to server")
            print("exit                        : shut all down")
            print("update_mods                 : update mods, available params are -log,-noreload,-quick")
            print("download [mod id]           : download mod, add \"required\" to command to make it required mod")
            print()

        help()

        while True:
            input_ = input(">>> ")

            if input_.startswith("/"):

                input_ = input_[1:]
                while input_[0] == " ": input_ = input_[1:]

                await asyncio.gather(write_stdin(var.server_proc.stdin, input_))


            else:
                msg = input_.split(" ")[0]

                if msg == "help":
                    help()

                if msg == "exit":
                    msg = "exit"
                    await asyncio.gather(write_stdin(var.server_proc.stdin, msg))
                    break

                if msg == 'update_mods':
                    log = False
                    noreload = False
                    quick = False
                    argv = input_.replace("update_mods", "").replace(" ","")
                    if "-" in argv:
                        argv = argv.replace("-",'')
                        if "log" in argv: log = True; argv = argv.replace("log","")
                        if "noreload" in argv: noreload = True; argv = argv.replace("noreload","")
                        if 'quick' in argv: quick = True; argv = argv.replace("quick","")

                        if len(argv) != 0:
                            print("Unknown parameter : %s" % (argv))
                        
                        else:
                            await update_mods(log=log, noreload=noreload, quick=quick)

                    else:
                        if len(argv) != 0:
                            print("Unknown parameter : %s" % (argv))
                            
                        else:
                            await update_mods(log=log, noreload=noreload, quick=quick)

                if msg == 'download':
                    mod_id = input_.replace("download","").replace("required","")
                    if "required" in input_:
                        required = True
                    else: required = False
                    try:
                        mod_id = int(mod_id)
                        if required: print("start downloading required mod")
                        else: print("start downloading whitelist mod")
                        log = await rimworld.download_mod(mod_id, required)
                        print("Downloaded mod!")
                    except Exception as e:
                        print("Incorrect mod id. \nMod id can be found at end of url, after filedetails/?id=")

                if msg == 'delete':
                    mod_id = input_.replace("delete","").replace(" ","")
                    print(f'Deleting mod {mod_id}')
                    msg = rimworld.delete_mod(mod_id)
                    print(f'{msg} {mod_id}')

                if msg == 'auto_update':
                    var.auto_update = not var.auto_update
                    if var.auto_update:
                        print("Auto update is now on")
                        update = Thread(target=update_task)
                        update.daemon = True
                        update.start()
                    else:
                        print("Auto update is now off\n Warning! Wait for task is closed message before restarting update!")

    else:
        print("Currently, all i can do for windows is to update mods due to mismatch of things.")
        print("see var.json for how to")
        input("Press enter to close")


if __name__ == '__main__':
    print_ = True
    asyncio.run(main())
    # main()