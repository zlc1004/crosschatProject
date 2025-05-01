import crosschat
import telegram
import threading
from typing import Union, Optional, Any

class TelegramPlatform(crosschat.Platform):
    def __init__(self, crosschat: crosschat.CrossChat):
        super().__init__(crosschat)
        self.name = "telegram"
        self.bot = telegram