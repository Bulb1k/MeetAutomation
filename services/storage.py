import os
import shutil
import logging

logger = logging.getLogger(__name__)

# Логіка для збереження файлів запису локально
class LocalFileStorage:
    def __init__(self, base_path: str = "recordings"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, local_path: str, destination_name: str) -> str:
        target_path = os.path.join(self.base_path, destination_name)
        try:
            shutil.move(local_path, target_path)
            logger.info(f"File saved locally at: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Failed save file locally: {e}")
            raise