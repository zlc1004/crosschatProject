import crosschat
from typing import Optional, Sequence, Coroutine
import telegram
import telegram.ext
import telegram._utils.types
import telegram._utils.defaultvalue
import signal
import threading
import platform
from rich import print


class TelegramPlatform(crosschat.Platform):
    def __init__(
        self, crosschat: crosschat.CrossChat, token: str, name: str = "telegram", 
    ):
        super().__init__(crosschat=crosschat, name=name)
        self.name = name
        self.app = telegram.ext.Application.builder().token(token).build()
        self.add_to_crosschat()
        self.logger = crosschat.logger
        self.thread = None

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

    async def run(self):
        self.app.add_handler(telegram.ext.CommandHandler("start", self.start))
        self.app.add_handler(telegram.ext.CommandHandler("data", self.updateData))
        await self.make_runner()

    async def send_message(self, channel: "Channel", content: str, user: "User", reply: Optional["OriginalMessage"] = None, attachments: list["Attachment"] = []) -> int:
        coroutine = self.app.bot.send_message(
            chat_id=channel.get_id(self.name), text=f"{user.get_name()}:\n{content}"
        )
        print(coroutine)
        print(f"Sending message to {self.name} channel {channel.get_id(self.name)}")
        result: telegram.Message = await coroutine
        print(f"Message sent to {self.name} channel {channel.get_id(self.name)}")
        return result.message_id

    def make_runner(self):
        poll_interval: float = 0.0
        timeout: int = 10
        bootstrap_retries: int = 0
        allowed_updates: Optional[Sequence[str]] = telegram.Update.ALL_TYPES
        drop_pending_updates: Optional[bool] = None
        close_loop: bool = True
        stop_signals: telegram._utils.types.ODVInput[Sequence[int]] = (
            telegram._utils.defaultvalue.DEFAULT_NONE
        )

        if not self.app.updater:
            raise RuntimeError(
                "Application.run_polling is only available if the application has an Updater."
            )

        def error_callback(exc: telegram.error.TelegramError) -> None:
            self.app.create_task(self.app.process_error(error=exc, update=None))

        # print("0")
        updater_coroutine = self.app.updater.start_polling(
            poll_interval=poll_interval,
            timeout=timeout,
            bootstrap_retries=bootstrap_retries,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            error_callback=error_callback,  # if there is an error in fetching updates
        )
        return self.__run(**{"updater_coroutine": updater_coroutine,
                "stop_signals": stop_signals,
                "bootstrap_retries": bootstrap_retries,
                "close_loop": close_loop})

    async def __run(
        self,
        updater_coroutine: Coroutine,
        stop_signals: telegram._utils.types.ODVInput[Sequence[int]],
        bootstrap_retries: int,
        close_loop: bool = True,
    ) -> None:
        if (
            stop_signals is telegram._utils.defaultvalue.DEFAULT_NONE
            and platform.system() != "Windows"
        ):
            stop_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT)
        self.logger.warning(
            "Skipping adding signal handlers for the stop signals.",
            stacklevel=3,
        )
        try:
            self.crosschat.run_coroutine(
                self.app._bootstrap_initialize(max_retries=bootstrap_retries)
            )
            # print("3")
            if self.app.post_init:
                self.crosschat.run_coroutine(self.app.post_init(self))
                # print("5")
            # if self.app.__stop_running_marker.is_set():
            #     self.app._LOGGER.info("Application received stop signal via `stop_running`. Shutting down.")
            #     return
            self.crosschat.run_coroutine(
                updater_coroutine
            )  # one of updater.start_webhook/polling
            # print("7")
            self.crosschat.run_coroutine(self.app.start())
            # print("9")
            while self.app.running:
                pass
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Application received stop signal. Shutting down.")
        finally:
            # We arrive here either by catching the exceptions above or if the loop gets stopped
            # In case the coroutine wasn't awaited, we don't need to bother the user with a warning
            updater_coroutine.close()
            try:
                # Mypy doesn't know that we already check if updater is None
                if self.app.updater.running:  # type: ignore[union-attr]
                    self.crosschat.run_coroutine(self.app.updater.stop())  # type: ignore[union-attr]
                if self.app.running:
                    self.crosschat.run_coroutine(self.app.stop())
                    # post_stop should be called only if stop was called!
                    if self.app.post_stop:
                        self.crosschat.run_coroutine(self.app.post_stop(self.app))
                self.crosschat.run_coroutine(self.app.shutdown())
                if self.app.post_shutdown:
                    self.crosschat.run_coroutine(self.app.post_shutdown(self.app))
            finally:
                pass

    async def exit(self):
        await self.app.stop()
        self.running = False

    def health_check(self):
        return self.app.running
