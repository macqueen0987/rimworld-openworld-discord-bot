# this file takes care of any variables that are used around other files

from json import loads
import requests

var_json = "https://raw.githubusercontent.com/macqueen0987/rimworld-openworld-discord-bot/main/var.json"
def init():

    try:
        with open("var.json") as jsonFile:
            Lines = jsonFile.readlines()
            jsonFile.close()
    except:
        print("cannot find var.json")

        response = requests.get(var_json).text
        with open("var.json", "w") as f:
            f.write(response)

        print("var.json created. please edit it!")
        input("Press enter to continue")
        exit()



    jsonObjects = ''
    for Line in Lines:
        Line = Line.replace(" ","")
        if Line.startswith("//") or Line.startswith("\n"):
            pass
        else:
            jsonObjects += Line

    jsonObjects = loads(jsonObjects)

    for jsonObject in jsonObjects:
        globals()[jsonObject] = jsonObjects[jsonObject]


if __name__ == '__main__':
    init()