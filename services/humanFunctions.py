def humanBitrate(bitrate_kbps):
    if bitrate_kbps > 10000:
        bitrate = str(round(bitrate_kbps/1000, 2)) + ' ' + 'Mb/s'
    else:
        bitrate = str(round(bitrate_kbps, 2)) + ' ' + 'kb/s'
    return bitrate


def humanSize(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')

def remove_N(seq):
    i = 1
    while i < len(seq):
        if seq[i] == seq[i-1]:
            del seq[i]
            i -= 1
        else:
            i += 1


print("Human functions loaded", flush=True)
