import logging
from enum import Enum
from seleniumbase import BaseCase

logger = logging.getLogger(__name__)

# unknown - якщо зустрічі немає (закінчився, не валідне помилання і тд.)
# lobby - на початку (вводу імені, налаштування камери та мікро)
# joined - приєднанні до зустрічі
# waiting - очікування оброки заявки на приєднання
class StatusMeet(Enum):
    JOINED = "joined"
    LOBBY = "lobby"
    WAITING = "waiting"
    UNKNOWN = "unknown"

# Саме автоматизація
class MeetClient:
    def __init__(self, sb: BaseCase):
        self.sb = sb
        self.bot_name = "Bot"

    def join_meeting(self, meet_url: str, bot_name: str = "Bot", turn_on_cam: bool = False, turn_on_mic: bool = False):
        self.bot_name = bot_name
        logger.info(f"Opening meeting: {meet_url}")

        # Виставлення анг мови сайту для
        if "?" in meet_url:
            meet_url += "&hl=en"
        else:
            meet_url += "?hl=en"

        self.sb.open(meet_url)
        self.sb.wait_for_ready_state_complete()

        self._turn_off_devices(turn_on_cam, turn_on_mic)
        self._enter_name(self.bot_name)
        self._click_join_button()

        self._wait_for_status_update()

    # Очікування зміни статусу
    def _wait_for_status_update(self):
        logger.info("Waiting for status update...")
        for _ in range(20):
            status = self.get_current_status()
            if status == StatusMeet.WAITING or status == StatusMeet.JOINED:
                return
            self.sb.sleep(0.5)

    # Вимкнення мікрофону та камери
    def _turn_off_devices(self, turn_on_cam: bool = False, turn_on_mic: bool = False):
        mic_btn = 'div[role="button"][data-is-muted="false"][aria-label*="microphone"]'
        cam_btn = 'div[role="button"][data-is-muted="false"][aria-label*="camera"]'

        if not turn_on_cam:
            self.sb.wait_for_element_visible(mic_btn)
            self.sb.click(mic_btn)
            logger.info("Microphone off click")

        if not turn_on_mic:
            self.sb.wait_for_element_visible(cam_btn)
            self.sb.click(cam_btn)
            logger.info("Camera off click")

    # Введення імені
    def _enter_name(self, name: str):
        name_input = 'input[type="text"][autocomplete="name"]'

        if self.sb.is_element_visible(name_input):
            self.sb.type(name_input, name)
            logger.info("Name entered")
        else:
            logger.info("Name input skipped")

    # Запрос на приєднення
    def _click_join_button(self):
        join_bt_selector = '//span[text()="Ask to join"]'

        self.sb.wait_for_element_visible(join_bt_selector)
        self.sb.click(join_bt_selector)

        logger.info("Clicked join")

    # Отримання статусу підключення
    def get_current_status(self) -> StatusMeet:
        # Якщо є токен сесії значить ми на зустрічі
        if self.sb.get_session_storage_item("persistent_token"):
            return StatusMeet.JOINED

        wait_text_long = '//div[contains(text(), "Please wait until a meeting host")]'
        wait_text_short = '//div[contains(text(), "Asking to be joined")]'

        # Якщо є текст на приєднання значить це очікування на приєдання
        if self.sb.is_element_visible(wait_text_long) or \
                self.sb.is_element_visible(wait_text_short):
            return StatusMeet.WAITING

        # Якщо є мікро або камери значить це лобі
        if self.sb.is_element_visible('//span[text()="Ask to join"]') or \
                self.sb.is_element_visible('//span[text()="Join now"]'):
            return StatusMeet.LOBBY

        return StatusMeet.UNKNOWN