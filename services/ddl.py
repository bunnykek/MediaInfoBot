import os
import re
import subprocess

from pyrogram.types import Message


URLRx = re.compile(r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])")
nameRx = re.compile(r".+/(.+)")
def ddlinfo(msg: Message):
    print("Got the DDL request!", flush=True)
    try:
        ddl = URLRx.search(msg.text).group(0)
        name = nameRx.search(ddl).group(1)
        gen_ddl_mediainfo(msg, ddl, name)

    except:
        print("Enter a valid ddl", flush=True) 
        raise Exception("`Something went wrong.\nPlease make sure you used a valid URL.`")
        


def gen_ddl_mediainfo(msg: Message, ddl:str, name:str):
    mediainfo = subprocess.check_output(['mediainfo', ddl]).decode("utf-8")
    lines = mediainfo.splitlines()
    for i in range(len(lines)):
        if 'Complete name' in lines[i]:
            lines[i] = re.sub(r": .+", ': '+name, lines[i])
            break
    with open(f'{name}.txt', 'w') as f:
        f.write('\n'.join(lines))
    
    #send the file
    msg.reply_document(f"{name}.txt")
    print("DDL file Mediainfo sent", flush=True)
    os.remove(f"{name}.txt")
    
print("ddl.py loaded", flush=True)
