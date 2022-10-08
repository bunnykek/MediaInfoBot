import os
import subprocess

from pyrogram.types import Message


def generateSpek(msg: Message):
    print("Got the audio spek request.")
    attatchment = msg.reply_to_message
    mediaType = attatchment.media.value
    print("mediatype:", mediaType)

    if 'audio' in mediaType:
        media = attatchment.audio
    elif 'document' in mediaType and 'audio' in attatchment.document.mime_type:
        media = attatchment.document
    else:
        print("Non audio file")
        raise Exception("Non-audio file!")

    fileName = media.file_name
    mime = media.mime_type

    attatchment.download(os.path.join(os.getcwd(), fileName))

    if 'm4a' in mime.lower() or 'audio/mp4' in mime.lower():  #for apple ALAC and AAC in m4a container
        subprocess.Popen(["ffmpeg", "-i", fileName, "-f",
                         "flac", fileName+'.flac']).wait()
        subprocess.Popen(["sox", fileName+'.flac', "-n", "remix", "1", "spectrogram", "-x", "1000",
                          "-y", "513", "-z", "120", "-w", "Kaiser", "-o", f"{fileName}.png"]).wait()
        os.remove(fileName+'.flac')
    else:
        subprocess.Popen(["sox", fileName, "-n", "remix", "1", "spectrogram", "-x", "1000",
                          "-y", "513", "-z", "120", "-w", "Kaiser", "-o", f"{fileName}.png"]).wait()
    os.remove(fileName)
    if not os.path.exists(f"{fileName}.png"):
        raise Exception(f"[{mime}] Spek cannot be generated for this file!")
    msg.reply_document(f"{fileName}.png", caption=f"`{fileName}`")
    os.remove(f"{fileName}.png")
