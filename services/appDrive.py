import os
import re

import requests
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import Message

from services.ddl import URLRx
from services.gDrive import downloadandsendGdrivefile, gdriveRe, get_gdrive_metadata

load_dotenv()

keyRx = re.compile(r'formData\.append\( \"key\", \"(.+)\" \)')
titleRx = re.compile(r"<title>(.+)</title>")
cookies = {
    'PHPSESSID': os.getenv('appdrive_php'),
    'MD': os.getenv('appdrive_md')
}

text = """AppDrive:
Filename: {}
Gdrive FileID: {}"""


def getKeyTitle(url):
    response = requests.get(url, cookies=cookies)
    key = re.search(keyRx, response.text).group(1)
    title = re.search(titleRx, response.text).group(1)
    print(key, flush=True)
    return (key, title)


def getDriveUrl(url, key):
    headers = {
        'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryExPHAhKfkkEG7paq',
    }

    data = f'------WebKitFormBoundaryExPHAhKfkkEG7paq\r\nContent-Disposition: form-data; name="action"\r\n\r\noriginal\r\n------WebKitFormBoundaryExPHAhKfkkEG7paq\r\nContent-Disposition: form-data; name="type"\r\n\r\n1\r\n------WebKitFormBoundaryExPHAhKfkkEG7paq\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n------WebKitFormBoundaryExPHAhKfkkEG7paq--\r\n'

    response_json = {'error': True}
    appdrive_file_id = url.split('/')[-1]
    for i in range(5):
        print(i, "time", flush=True)
        if response_json['error']:
            response = requests.post(
                f'https://appdrive.info/file/{appdrive_file_id}', cookies=cookies, headers=headers, data=data)
            #print(response.text, flush=True)
            try:
                response_json = response.json()
                if not response_json['error']:
                    break
            except:
                continue
    try:
        print(response.json()['url'], flush=True)
        return response.json()['url']
    except:
        return None


def appdriveInfo(msg: Message, client: Client):
    print("Got the appdrive request!", flush=True)
    url = URLRx.search(msg.text).group(0)
    key, title = getKeyTitle(url)

    driveurl = getDriveUrl(url, key)
    if driveurl == None:
        raise Exception("Something went wrong with appdrive.")

    fileid = gdriveRe.search(driveurl).group(1)
    print(text.format(title, fileid), flush=True)
    print("Fetching metadata using Gdrive API.", flush=True)
    metadata = get_gdrive_metadata(fileid)
    print(metadata, flush=True)
    print("Forwarding further processing of ID to Gdrive module")
    downloadandsendGdrivefile(msg, fileid, client)
    print("Appdrive MediaInfo done.", flush=True)

print("AppDrive loaded", flush=True)
