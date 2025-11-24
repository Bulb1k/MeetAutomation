import logging
import time
import os
from seleniumbase import SB
from services.google_meet import MeetClient, StatusMeet
from config import BOT_NAME, INVITE_LINK, STORAGE_PATH, CHROME_ARGS, HEADLESS, RECORDING, CAMERA, MICROPHONE, AUDIO, \
    LOG_LEVEL, LOG_FORMAT
from services.recorder import ScreenRecorder
from services.storage import LocalFileStorage

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"DEBUG: Saving files to: {STORAGE_PATH}")
    if not INVITE_LINK or INVITE_LINK.strip() == "":
        logger.error("INVITE_LINK is empty")
        return
    # Ініціалізація класу для роботи з файлами та записку відео
    storage = LocalFileStorage(base_path=STORAGE_PATH)
    recorder = ScreenRecorder()

    # Тимчасового файли для запису відео (формат .mkv більш витривалий до пошкоджень)
    with SB(uc=True, headless=HEADLESS, chromium_arg=",".join(CHROME_ARGS)) as sb:
        client = MeetClient(sb)

        try:
            if RECORDING:
                temp_filename = f"temp_rec_{int(time.time())}.mkv"
                temp_path = f"{STORAGE_PATH}/tmp/{temp_filename}"

                recorder.start_recording(temp_path, audio=AUDIO)

                logger.info("Starting recording...")

            # Приєднання до Google Meet
            client.join_meeting(INVITE_LINK, BOT_NAME, CAMERA, MICROPHONE)

            # Очікування підтвердження приєднання
            while client.get_current_status() == StatusMeet.WAITING:
                logger.info("Waiting for join permission...")
                sb.sleep(5)

            # Обробка відхилення приєднання
            if client.get_current_status() != StatusMeet.JOINED:
                logger.error("Meet join declined or ended")
                return

            logger.info("Meet joined")

            # Очікування закінчення зустрічі
            while client.get_current_status() == StatusMeet.JOINED:
                sb.sleep(5)

            logger.info("Meet ended")

        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Збереження запису з тимчасового
            if RECORDING:
                logger.info("Stopping recording...")
                recorder.stop_recording()

                if os.path.exists(temp_path):
                    # Збереження запису в mp4
                    final_filename = f"rec_{int(time.time())}.mp4"
                    storage.save(temp_path, final_filename)
                    logger.info(f"Saved: {final_filename}")
                else:
                    logger.warning("File not found")


if __name__ == "__main__":
    main()