import os
import sys

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

from services.appDrive import appdriveInfo
from services.appleMusic import amInfo
from services.ddl import ddlinfo
from services.gDrive import gdriveInfo
from services.gdtot import gdtotInfo
from services.mega import megaInfo
from services.sox import generateSpek
from services.tgFile import tgInfo

load_dotenv()

#sys.path.append(os.path.join(os.getcwd(), 'services'))


helpMessage = """MediaInfo support the following services:
`• G-DRIVE
• MEGA.nz
• AppDrive
• GDTOT
• Direct download links
• Telegram files`

**Example:**
For MediaInfo:
`/info url`
`reply /info to file`

For audio Spek:
`reply /spek to audio`

For AppleMusic album info:
`/info album_url`

Made by @pseudoboi🧪"""


owner = str(os.getenv('owner'))

app = Client('botsession', api_id=os.getenv('api_id'),
             api_hash=os.getenv('api_hash'),
             bot_token=os.getenv('bot_token'))

print("MediaInfo bot started!", flush=True)


@app.on_message(filters.text & filters.private)
def hello(client: Client, message: Message):
    if message.from_user.id == owner:
        message.reply("Unauthorized!!!")
        return

    if '/start' in message.text:
        message.reply("Send /help for more info.")
        return

    if '/help' in message.text:
        message.reply(helpMessage)
        return

    try:
        if "/spek" in message.text:
            message.reply("Processing your spectrogram request...")
            generateSpek(message)
            return

        elif "/info" in message.text:
            if 'mega.nz' in message.text.lower():
                message.reply("Processing your MEGA.nz request...")
                megaInfo(message, app)
            elif 'drive.google' in message.text.lower():
                message.reply("Processing your G-DRIVE request...")
                gdriveInfo(message, app)
            elif 'appdrive' in message.text.lower():
                message.reply("Processing your AppDrive request...")
                appdriveInfo(message, app)
            elif 'gdtot' in message.text.lower():
                message.reply("Processing your GDTOT request...")
                gdtotInfo(message, app)
            elif 'music.apple' in message.text.lower():
                amInfo(message)
            elif message.reply_to_message:
                message.reply("Processing your Telegram file request...")
                tgInfo(client, message)
            elif len(message.text) > 10:
                message.reply("Processing your DDL request...")
                ddlinfo(message)
    except Exception as e:
        message.reply(f"`An error occured!`\n{e}")
        print(e, flush=True)
        return


app.run()
