import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

######
OPENAI_API_KEY = "sk-"
OPENAI_API_BASE = ""
OPENAI_MODEL = "gpt-4o"  # gpt-4o-mini
#####

FFMPEGPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "ffmpeg.exe"
)
TEMP_PATH = os.getenv("TEMP_PATH", "./tmp")
ASSETS_PATH = os.getenv("ASSETS_PATH", "./videos")
AUTO_SAVE_INTERVAL = int(os.getenv("AUTO_SAVE_INTERVAL", 100))
SKIP_PATH = tuple(os.getenv("SKIP_PATH", "/tmp").split(","))
IGNORE_STRINGS = tuple(
    os.getenv("IGNORE_STRINGS", "thumb,avatar,__MACOSX,icons,cache").lower().split(",")
)
VIDEO_EXTENSIONS = tuple(
    os.getenv("VIDEO_EXTENSIONS", ".mp4,.flv,.mov,.mkv,.m4v").split(",")
)
SRT_FILE = (".srt", ".SRT")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", 8001)
CURRENT_VERSION = os.getenv("CURRENT_VERSION", "v0.1.3")
BASE_API_HOST = os.getenv("BASE_API_HOST", "http://127.0.0.1:5000")
