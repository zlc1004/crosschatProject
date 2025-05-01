import crosschat
import telegram
import threading
from typing import Union, Optional, Any

import telegram
import telegram.ext


class TelegramPlatform(crosschat.Platform):
    def __init__(
        self, crosschat: crosschat.CrossChat, token: str, name: str = "telegram"
    ):
        super().__init__(crosschat=crosschat, name=name)
        self.name = name
        self.app = telegram.ext.Application.builder().token(token).build()
        self.thread = threading.Thread(
            target=self.app.run_polling,
            kwargs={"allowed_updates": telegram.Update.ALL_TYPES},
            daemon=True,
        )
        self.running = False
        self.add_to_crosschat()

    async def start(
        update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=telegram.ForceReply(selective=True),
        )

    async def updateData(
        update: telegram.Update, context: telegram.ext.ContextTypes.DEFAULT_TYPE
    ) -> None:
        await update.message.reply_text(update.effective_chat.id)

    def run(self):
        self.app.add_handler(telegram.ext.CommandHandler("start", self.start))
        self.app.add_handler(telegram.ext.CommandHandler("data", self.updateData))
        self.thread.start()

    def exit(self):
        self.app.stop()
        self.thread.join()
        self.running = False

    def health_check(self):
        return self.app.running
