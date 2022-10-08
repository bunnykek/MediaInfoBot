import json
import os
import re
import subprocess
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.types import Message

from services.humanFunctions import humanBitrate, remove_N

load_dotenv()


megaRx = re.compile(r'mega.nz/file/(.+?)#(.+?)$')
fileNameRx = re.compile(r"(.+):")
sizeRx = re.compile(r"(.+) (GB|MB)")


def megaInfo(msg: Message, client: Client):
    print("Got the mega request.", flush=True)
    matches = re.search(megaRx, msg.text)
    if not matches:
        print("Invalid mega file link format", flush=True)
        raise Exception(
            "`Send mega.nz public file link in proper format.\nhttps://mega.nz/file/XXXXXXXX#YYYYYYYYYYYY`")

    fileId = matches.group(1)
    key = matches.group(2)

    print("Getting the file size", flush=True)
    size_kb, size_readable = getSize(f"https://mega.nz/file/{fileId}#{key}")
    if not size_kb or not size_readable:
        raise Exception("Unable to fetch the file size")

    print("megadl subprocess started", flush=True)
    pro = subprocess.Popen(['megadl', '--print-names',
                           '--path', f'.megatmp.{fileId}', f'https://mega.nz/#!{fileId}!{key}'], stdout=subprocess.PIPE)
    time.sleep(3)
    pro.terminate()

    try:
        fileName = pro.communicate()[0].decode("utf-8").partition("\n")[0]
        fileName = fileNameRx.search(fileName).group(1)
        print(fileName, flush=True)

        mediainfo = subprocess.check_output(
            ['mediainfo', f'.megatmp.{fileId}']).decode("utf-8")
        mediainfo_json = json.loads(subprocess.check_output(
            ['mediainfo', f'.megatmp.{fileId}', '--Output=JSON']).decode("utf-8"))
        duration = float(mediainfo_json['media']['track'][0]['Duration'])

        bitrate_kbps = size_kb/duration
        bitrate = humanBitrate(bitrate_kbps)

        # print(bitrate)

        lines = mediainfo.splitlines()
        for i in range(len(lines)):
            if 'Complete name' in lines[i]:
                lines[i] = re.sub(r": \..+", ': '+fileName, lines[i])
            elif 'File size' in lines[i]:
                lines[i] = re.sub(r": .+", ': '+size_readable, lines[i])
            elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:
                lines[i] = re.sub(r": .+", ': '+bitrate, lines[i])
            elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
                lines[i] = ''
        remove_N(lines)

        # save the list to a file
        with open(f'{fileName}.txt', 'w') as f:
            f.write('\n'.join(lines))

        msg.send_document(document=f'{fileName}.txt', caption=f'`{fileName}`')

        print("mega File mediainfo sent", flush=True)
        os.remove(f'{fileName}.txt')
    except:
        msg.reply(
            "Either you have sent a non-video/non-audio URL,\nor the link does not exist.")
        print("Either you have sent a non-video/non-audio URL,or the link does not exist", flush=True)
    finally:
        os.remove(f'.megatmp.{fileId}')


def getSize(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'lxml')
    temp = soup.find_all("meta")[0]["content"]
    search = sizeRx.search(temp)
    if not search:
        return None, None
    size, unit = search.groups()
    print(size, unit, flush=True)
    if unit == 'GB':
        return (float(size) * 8 * 1000000, size+' '+unit)
    elif unit == 'MB':
        return (float(size) * 8 * 1000, size+' '+unit)
    else:
        return (None, None)


print("mega.py loaded", flush=True)
