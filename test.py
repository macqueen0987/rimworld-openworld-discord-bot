import requests
from bs4 import BeautifulSoup

import var
import rimworld


def get_modcollection():
    url = 'https://steamcommunity.com/sharedfiles/filedetails/?id=2795309524'
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
