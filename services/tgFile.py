import json
import os
import re
import subprocess

from pyrogram import Client
from pyrogram.types import Message

from services.humanFunctions import humanBitrate, humanSize, remove_N

def tgInfo(client: Client, msg: Message):
    print("processing TG", flush=True)
    message = msg.reply_to_message
    # print(message)
    mediaType = message.media.value
    if mediaType == 'video':
        media = message.video
    elif mediaType == 'audio':
        media = message.audio
    elif mediaType == 'document':
        media = message.document
    else:
        print("This media type is not supported", flush=True)
        raise Exception("`This media type is not supported`")

    mime = media.mime_type
    fileName = media.file_name
    size = media.file_size

    print(fileName, size, flush=True)

    if mediaType == 'document':
        if 'video' not in mime and 'audio' not in mime and 'image' not in mime:
            print("Makes no sense", flush=True)
            raise Exception("`This file makes no sense to me.`")

    if int(size) <= 50000000:
        message.download(os.path.join(os.getcwd(), fileName))

    else:
        for chunk in client.stream_media(message, limit=5):
            # save these chunks to a file
            with open(fileName, 'ab') as f:
                f.write(chunk)

    mediainfo = subprocess.check_output(
        ['mediainfo', fileName]).decode("utf-8")

    mediainfo_json = json.loads(subprocess.check_output(
        ['mediainfo', fileName, '--Output=JSON']).decode("utf-8"))

    # write a function to convert bytes to readable format
    readable_size = humanSize(size)

    try:
        lines = mediainfo.splitlines()
        if 'image' not in mime:
            duration = float(mediainfo_json['media']['track'][0]['Duration'])
            bitrate_kbps = (size*8)/(duration*1000)
            bitrate = humanBitrate(bitrate_kbps)
            for i in range(len(lines)):
                if 'File size' in lines[i]:
                    lines[i] = re.sub(r": .+", ': '+readable_size, lines[i])
                    continue
                elif 'Overall bit rate' in lines[i] and 'Overall bit rate mode' not in lines[i]:
                    lines[i] = re.sub(r": .+", ': '+bitrate, lines[i])
                    continue
                elif 'IsTruncated' in lines[i] or 'FileExtension_Invalid' in lines[i]:
                    lines[i] = ''
                    continue

            remove_N(lines)

        with open(f'{fileName}.txt', 'w') as f:
            f.write('\n'.join(lines))

        msg.send_document(document=f'{fileName}.txt', caption=f'`{fileName}`')

        print("TG file Mediainfo sent", flush=True)
        os.remove(f'{fileName}.txt')
    except:
        message.reply_text(
            "Something bad occurred particularly with this file.")
        print("Something bad occurred for tg file", flush=True)
    finally:
        os.remove(fileName)


print("TG file module loaded", flush=True)
