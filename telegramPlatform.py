import crosschat
from typing import Optional, Sequence, Coroutine
import telegram
import telegram.ext
import telegram._utils.types
import telegram._utils.defaultvalue
import signal
import telegram._utils.warnings
import platform
import logging
import threading


class TelegramPlatform(crosschat.Platform):
    def __init__(
        self, crosschat: crosschat.CrossChat, token: str, name: str = "telegram"
    ):
        super().__init__(crosschat=crosschat, name=name)
        self.name = name
        self.app = telegram.ext.Application.builder().token(token).build()
        self.add_to_crosschat()
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        logging.getLogger("httpx").setLevel(logging.WARNING)
        self.logger = logging.getLogger(__name__)
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

    def run(self):
        self.app.add_handler(telegram.ext.CommandHandler("start", self.start))
        self.app.add_handler(telegram.ext.CommandHandler("data", self.updateData))
        self.makethread()
        self.thread.start()

    def send_message(self, channel, content, user, reply = None, attachments = ...):
        coroutine = self.app.bot.send_message(
                chat_id=channel.get_id(self.name),
                text=f"{user.get_name()}:\n{content}"
        )
        self.crosschat.run_coroutine(coroutine)
    

    def makethread(self):
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

        print("0")
        updater_coroutine = self.app.updater.start_polling(
            poll_interval=poll_interval,
            timeout=timeout,
            bootstrap_retries=bootstrap_retries,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            error_callback=error_callback,  # if there is an error in fetching updates
        )

        self.thread = threading.Thread(
            target=self.__run,
            kwargs={
                "updater_coroutine": updater_coroutine,
                "stop_signals": stop_signals,
                "bootstrap_retries": bootstrap_retries,
                "close_loop": close_loop,
            },
        )

    def __run(
        self,
        updater_coroutine: Coroutine,
        stop_signals: telegram._utils.types.ODVInput[Sequence[int]],
        bootstrap_retries: int,
        close_loop: bool = True,
    ) -> None:
        # Calling get_event_loop() should still be okay even in py3.10+ as long as there is a
        # running event loop, or we are in the main thread, which are the intended use cases.
        # See the docs of get_event_loop() and get_running_loop() for more info
        loop = self.crosschat.loop

        if (
            stop_signals is telegram._utils.defaultvalue.DEFAULT_NONE
            and platform.system() != "Windows"
        ):
            stop_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGABRT)
        # print("1")
        # try:
        #     if not isinstance(stop_signals, telegram._utils.defaultvalue.DefaultValue):
        #         for sig in stop_signals or []:
        #             loop.add_signal_handler(sig, self.app._raise_system_exit)
        # except NotImplementedError as exc:
        #     telegram._utils.warnings.warn(
        #         f"Could not add signal handlers for the stop signals {stop_signals} due to "
        #         f"exception `{exc!r}`. If your event loop does not implement `add_signal_handler`,"
        #         " please pass `stop_signals=None`.",
        #         stacklevel=3,
        #     )
        telegram._utils.warnings.warn(
            "Skipping adding signal handlers for the stop signals.",
            stacklevel=3,
        )
        print("2")
        try:
            self.crosschat.run_coroutine(
                self.app._bootstrap_initialize(max_retries=bootstrap_retries)
            )
            print("3")
            if self.app.post_init:
                self.crosschat.run_coroutine(self.app.post_init(self))
                print("5")
            # if self.app.__stop_running_marker.is_set():
            #     self.app._LOGGER.info("Application received stop signal via `stop_running`. Shutting down.")
            #     return
            self.crosschat.run_coroutine(
                updater_coroutine
            )  # one of updater.start_webhook/polling
            print("7")
            self.crosschat.run_coroutine(self.app.start())
            print("9")
            while self.app.running:
                pass
        except (KeyboardInterrupt, SystemExit):
            self.app._LOGGER.debug("Application received stop signal. Shutting down.")
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

    def exit(self):
        task = self.crosschat.loop.create_task(self.app.stop())
        self.crosschat.wait_for_task(task)
        self.thread.join()
        self.running = False

    def health_check(self):
        return self.app.running
