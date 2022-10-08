import base64
import os
import re

import requests
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import Message

from services.ddl import URLRx
from services.gDrive import downloadandsendGdrivefile

load_dotenv()

gtidRx = re.compile(r'file/(\d+)?')
gdRx = re.compile(r'200&gd=(.+)&')
gdriveRx = re.compile(r'https://drive\.google\.com/open\?id=(.+?)\"')
gdtotTitleRx = re.compile(r'<title>GDToT \| (.+)</title>')

Cookies = {
    'PHPSESSID': "",
    'crypt': f"{os.getenv('gdtot_crypt')}"
}


def updateCookie():
    response = requests.get('https://new.gdtot.xyz/', cookies=Cookies)
    Cookies['PHPSESSID'] = response.cookies.get_dict()['PHPSESSID']


def getGd(gtid):

    params = {
        'id': f'{gtid}'
    }

    for _ in range(3):
        response = requests.get(
            'https://new.gdtot.xyz/dld', params=params, cookies=Cookies)
        if 'you must login' in response.text:
            print("Cookie error, retrying...", flush=True)
            updateCookie()
            continue
        else:
            break

    print(response.text, flush=True)
    gd = re.search(gdRx, response.text).group(1)
    return gd


def gdtotInfo(msg: Message, client: Client):
    print("Got the gdtot request.", flush=True)
    url = URLRx.search(msg.text).group(0)
    print(url, flush=True)
    title = getTitle(url)
    print(title, flush=True)

    gtid = re.search(gtidRx, msg.text).group(1)
    driveid = base64.b64decode(getGd(gtid)).decode("utf-8")
    downloadandsendGdrivefile(msg, driveid, client)


def getTitle(url):
    response = requests.get(url)
    title = re.search(gdtotTitleRx, response.text).group(1)
    return title


print("gdtot.py loaded", flush=True)
