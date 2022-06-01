import random

import eel
import os
import subprocess
import inspect
import sys

from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


# Переменные
MAIN_URL = ""
FIRST_TIMING = -1
SECOND_TIMING = -1

MAIN_DIR = ""
TEMP_PATH = "C:\\Program Files\\Temp"
VIDEO_PATH = ""
VIDEOS_DIR_PATH = ""


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def download_from_youtube(url, path):
    yt = YouTube(url)
    yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not os.path.exists(path):
        os.makedirs(path)
    return yt.download(path)


def cut_video():
    id = random.randint(1000, 9999)
    ffmpeg_extract_subclip(VIDEO_PATH, FIRST_TIMING, SECOND_TIMING, targetname=VIDEOS_DIR_PATH + f"\\Cutted{id}.mp4")
    subprocess.Popen(rf'explorer /select,"{VIDEOS_DIR_PATH}"')


@eel.expose
def check_for_youtube_url(value):
    if "https://" not in value:
        return False
    if ".com" in value:
        return "youtube.com" in value and len(value) == 43
    if ".be" in value:
        return "youtu.be" in value and len(value) == 28
    return False


@eel.expose
def set_url(value):
    global MAIN_URL
    if check_for_youtube_url(value):
        MAIN_URL = value
        return True
    return False


@eel.expose
def get_url():
    return MAIN_URL


@eel.expose
def get_embed_url():
    video_id = get_video_id()
    return "https://www.youtube.com/embed/" + str(video_id)


@eel.expose
def get_video_id():
    if not check_for_youtube_url(MAIN_URL):
        return ""
    video_id = ""
    if ".com/watch?v=" in MAIN_URL:
        video_id = MAIN_URL.split(".com/watch?v=")[1]
    if "tu.be/" in MAIN_URL:
        video_id = MAIN_URL.split("tu.be/")[1]
    if "?" in video_id:
        video_id = video_id.split("?")[0]
    return str(video_id)


@eel.expose
def set_first_timing(value):
    global FIRST_TIMING
    FIRST_TIMING = float(value)


@eel.expose
def set_second_timing(value):
    global SECOND_TIMING
    SECOND_TIMING = float(value)


@eel.expose
def check_timings_correct():
    global FIRST_TIMING, SECOND_TIMING
    if FIRST_TIMING != -1 and SECOND_TIMING != -1:
        FIRST_TIMING = min(FIRST_TIMING, SECOND_TIMING)
        SECOND_TIMING = max(FIRST_TIMING, SECOND_TIMING)
        return True
    return False


@eel.expose
def download_video():
    global VIDEO_PATH
    VIDEO_PATH = download_from_youtube(MAIN_URL, TEMP_PATH)
    cut_video()
    return True


def main():
    global MAIN_DIR, VIDEOS_DIR_PATH

    MAIN_DIR = get_script_dir()
    VIDEOS_DIR_PATH = MAIN_DIR + "\\Videos"
    if not os.path.isdir(VIDEOS_DIR_PATH):
        os.mkdir(VIDEOS_DIR_PATH)

    size = (600, 400)
    port = 25550
    args = ['--incognito', '--no-experiments']

    eel.init("Web")
    eel.start("Start.html", size=size, cmdline_args=args, port=port)
    pass


if __name__ == "__main__":
    main()
