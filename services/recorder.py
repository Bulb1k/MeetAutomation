import os
import subprocess
import signal
import logging
import time

logger = logging.getLogger(__name__)


# Клас для роботи з FFmpeg та запису аудіо. Не викристав вбудований FFmpeg від SeleniumBase тому що немає змоги записувати аудіо
class ScreenRecorder:
    def __init__(self):
        self.process = None
        self.output_file = None

    def start_recording(self, output_file: str, audio: bool = True):
        self.output_file = output_file

        # Беремо дисплей який створив SeleniumBase
        current_display = os.getenv("DISPLAY", ":99")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Базова команда (відео вхід)
        command = [
            "ffmpeg",
            "-y",
            "-f", "x11grab",
            "-framerate", "30",
            "-draw_mouse", "1",
            "-i", f"{current_display}+0,0",
        ]

        # Додаємо аудіо вхід та налаштування
        if audio:
            command.extend([
                "-f", "pulse",
                "-i", "v1.monitor",
                "-c:a", "aac",
                "-b:a", "128k",
                "-ar", "44100",
            ])

        # Додаємо налаштування відео кодека та вихідний файл
        command.extend([
            "-c:v", "libx264",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_file
        ])

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(2)

        if self.process.poll() is not None:
            stdout, stderr = self.process.communicate()
            logger.debug(f"STDERR: {stderr}")
            raise RuntimeError(f"FFmpeg failed to start")

        logger.info(f"FFmpeg started)")

    def stop_recording(self):
        if not self.process:
            logger.warning("No active recording to stop.")
            return

        logger.info("Stopping recording...")
        self.process.send_signal(signal.SIGINT)

        try:
            # Чекаємо до 10 секунд на завершення процесу
            self.process.communicate(timeout=10)
            logger.info(f"Recording saved: {self.output_file}")
        except subprocess.TimeoutExpired:
            # Якщо FFmpeg завис — вбиваємо процес примусово
            logger.warning("FFmpeg stuck. Killing...")
            self.process.kill()
            self.process.communicate()

        self.process = None

    def is_recording(self) -> bool:
        return self.process is not None and self.process.poll() is None