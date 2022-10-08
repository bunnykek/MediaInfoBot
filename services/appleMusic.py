import re

import m3u8
import requests
from pyrogram.types import Message

apple_rx = re.compile(r"apple\.com\/(\w\w)\/album\/.+\/(\d+|pl\..+)")


headers = {
    'origin': 'https://music.apple.com',
    'Authorization': 'Bearer pppppppppppppppppp',
}

params = {
    'extend': 'extendedAssetUrls',
}

def updateToken():
    response = requests.get("https://music.apple.com/us/album/positions-deluxe-edition/1553944254")
    headers['Authorization'] = f'Bearer {re.search(r"(eyJhbGc.+?)%22%7D", response.text).group(1)}' 


def amInfo(message: Message):
    # result = apple_rx.search(message)
    result = apple_rx.search(message.text)
    if not result:
        message.reply("`Improper Apple Music album URL!`")
        return
    region, id_ = result.groups()
    response = requests.get(f'https://amp-api.music.apple.com/v1/catalog/{region}/albums/{id_}/', params=params, headers=headers)
    if response.status_code == 401:
        print("Updating token!")
        updateToken()
        response = requests.get(f'https://amp-api.music.apple.com/v1/catalog/{region}/albums/{id_}/', params=params, headers=headers)
    info = response.json()['data'][0]
    release_date = info['attributes']['releaseDate']
    adm = 'True' if info['attributes']['isMasteredForItunes'] else 'False'
    url = info['attributes']['url']
    name = info['attributes']['name']
    print(name)
    artist = info['attributes']['artistName']
    traits = info['attributes']['audioTraits']
    artwork = info['attributes']['artwork']['url']
    w = str(info['attributes']['artwork']['width'])
    h = str(info['attributes']['artwork']['height'])

    print(traits)
    hls = info['relationships']['tracks']['data'][0]['attributes']['extendedAssetUrls']['enhancedHls']
    #print(hls)
    playlist = m3u8.parse(m3u8.load(hls).dumps())
    alacs = []
    for stream in playlist['playlists']:
        if stream['stream_info']['codecs'] == 'alac':
            temp = stream['stream_info']['audio'].split('-')
            sr = int(temp[-2])/1000
            depth = int(temp[-1])
            alacs.append((sr, depth))
    alacs.sort()
    #print(alacs)
    codecs = ["Lossy AAC"]
    if 'atmos' in traits:
        codecs.append("Dolby Atmos")
    if 'lossless' in traits:
        for i,j in alacs:
            codecs.append(f"ALAC {i}-{j}")

    text = f"""Album  : **[{name}]({url}) | [{w}x{h}]({artwork.format(w=w,h=h)})**
Artist    : **{artist}**
Date     : **{release_date}**
Codecs: **{' | '.join(codecs)}**
Apple Digital Masters: **{adm}**"""
    message.reply_photo(photo=artwork.format(w=w,h=h), caption=text)
    print("AppleMusic album info done.")

print("appleMusic loaded", flush=True)