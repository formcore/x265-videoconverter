#!/usr/bin/env python3
import os
import subprocess
import logging

def videoCodecName(file):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", file]
    output = subprocess.check_output( cmd )
    return output.strip().decode('ascii')

def mediaList():
    videoList = []
    directoryList = []
    for directory in os.listdir(os.getcwd()):
        if os.path.isdir(directory) and not directory.endswith('.old'):
            directoryList.append(os.path.abspath(directory))

    for directory in directoryList:
        for file in os.listdir(directory):
            filepath = os.path.join(directory, file)
            filename = file.lower()
            if not (filename.endswith('.mkv') or filename.endswith('.mp4')):
                continue
            encoding = videoCodecName(filepath)
            if not encoding == 'hevc':
                logging.info('adding file: %s', filepath)
                logging.info('codec: %s', encoding)
                videoList.append(filepath)
            if len(videoList) >= 10:
                return videoList
    return videoList

def backup(fullpath):
    backupDirectory = os.path.dirname(fullpath)+'.old'
    if not os.path.exists(backupDirectory):
        os.makedirs(backupDirectory)
    newFilePath = os.path.join(backupDirectory, os.path.basename(fullpath))
    os.rename(fullpath, newFilePath)
    return newFilePath

def convertLibx265(input, output):
    cmd = ["ffmpeg", "-i", input, "-n", "-ac", "2", "-map", "0", "-c:v", "libx265", "-c:a", "aac", "-c:s", "copy", output]
    result = subprocess.call(cmd)
    return result

logging.basicConfig(filename='h265encode.py.log', level=logging.DEBUG)

for file in mediaList():
    logging.info('converting file %s', file)
    print(file)
    input = backup(file)
    print(input)
    output = os.path.splitext(file)[0]+'.mkv'
    result = convertLibx265(input, output)
    if result == 0:
        print("delete: "+input)
        logging.info('delete: %s', input)
        os.remove(input)
    else:
        logging.warning('failed to convert %s \n error code: %s', input, result)
        logging.warning('Delete %s', output)
        logging.warning('replace %s', file)
        os.remove(output)
        os.rename(input, file)
    print(result)
