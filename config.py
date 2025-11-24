import logging
from environs import Env
from pathlib import Path

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent

INVITE_LINK: str = env.str("INVITE_LINK")
BOT_NAME: str = env.str("BOT_NAME")

MICROPHONE: bool = env.bool("MICROPHONE")
CAMERA: bool = env.bool("CAMERA")

RECORDING: bool = env.bool("RECORDING")
AUDIO: bool = env.bool("AUDIO")

HEADLESS: bool = env.bool("HEADLESS")

STORAGE_DIR = env.str("STORAGE_DIR", "recordings")
STORAGE_PATH = str(BASE_DIR / STORAGE_DIR)

CHROME_ARGS = [
    "--kiosk",
    "--disable-gpu",
    "--no-sandbox",
    "--use-fake-ui-for-media-stream",
    "--use-fake-device-for-media-stream",
]

LOG_LEVEL = env.str("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s %(name)s: %(message)s"