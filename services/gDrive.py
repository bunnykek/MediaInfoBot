import json
import os
import re
import subprocess

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pyrogram import Client
from pyrogram.types import Message

from services.humanFunctions import humanBitrate, humanSize, remove_N

tokenJson = json.loads(os.getenv('token_json'))

gdriveRe = re.compile('([-\w]{25,})')

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = Credentials.from_authorized_user_info(tokenJson, SCOPES)
service = build('drive', 'v3', credentials=creds)


def gdriveInfo(msg: Message, client: Client):
    print("Got the Gdrive request.", flush=True)
    match = re.search(gdriveRe, msg.text)
    if not match:
        print("Send a proper GDRIVE public file link!", flush=True)
        raise Exception("Send a proper/accessible GDRIVE file URL.")
    fileid = match.group(1)
    downloadandsendGdrivefile(msg, fileid, client)


def get_gdrive_metadata(fileid):
    metadata = service.files().get(fileId=fileid, fields='name, size, mimeType',
                                   supportsAllDrives=True).execute()
    return metadata


def downloadandsendGdrivefile(msg: Message, fileid, client: Client):
    request = service.files().get_media(fileId=fileid)
    metadata = get_gdrive_metadata(fileid)
    print(metadata, flush=True)

    fname = metadata['name']

    if not 'video' in metadata['mimeType'] and not 'audio' in metadata['mimeType']:
        print("File made no sense", flush=True)
        raise Exception("`This file makes no sense to me.`")

    f = open(f"{fileid}", "wb")
    downloader = MediaIoBaseDownload(f, request)
    print("way to loop", flush=True)
    try:
        for i in range(2):
            downloader.next_chunk()
        f.close()
    except ValueError as v:
        print(v, flush=True)
    print("Downloaded the first 2 chunk.", flush=True)

    mediainfo = subprocess.check_output(
        ['mediainfo', fileid]).decode("utf-8")
    mediainfo_json = json.loads(subprocess.check_output(
        ['mediainfo', fileid, '--Output=JSON']).decode("utf-8"))
    duration = float(mediainfo_json['media']['track'][0]['Duration'])
    bitrate_kbps = float(metadata['size'])*8/(duration * 1000)
    bitrate = humanBitrate(bitrate_kbps)

    size_readable = humanSize(float(metadata['size']))
    print("Got the file size", flush=True)

    # print(bitrate)
    lines = mediainfo.splitlines()
    for i in range(len(lines)):
        if 'Complete name' in lines[i]:
            lines[i] = re.sub(r": .+", ': '+metadata['name'], lines[i])
        elif 'File size' in lines[i]:
            lines[i] = re.sub(r": .+", ': '+size_readable, lines[i])
        elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:
            lines[i] = re.sub(r": .+", ': '+bitrate, lines[i])
        elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
            lines[i] = ''
    remove_N(lines)

    # save the list to a file
    with open(f"{fname}.txt", 'w') as f:
        f.write('\n'.join(lines))

    msg.reply_document(document=f'{fname}.txt', caption=f'`{fname}`')

    os.remove(f"{metadata['name']}.txt")
    os.remove(fileid)
    print("G-Drive file mediainfo sent", flush=True)


print("Gdrive loaded", flush=True)
