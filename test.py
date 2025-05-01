import crosschat
import discordPlatform
import time

with open("./tokens/test", "r") as f:
    botToken = f.read().strip()


class TelegramPlatform(crosschat.Platform):
    def __init__(self, crosschat):
        super().__init__(crosschat)
        self.name = "telegram"


app = crosschat.CrossChat()
discord = discordPlatform.DiscordPlatform(app, botToken)
discord.add_to_crosschat()
telegram = TelegramPlatform(app)
telegram.add_to_crosschat()

channel = crosschat.Channel(app, "general")

channel.set_id("discord", 1367251777606385777)
channel.set_id("telegram", 200)
channel.set_extra_data(
    "discord_webhook",
    discord.make_webhook(
        "1367254260684951602",
        "WP_XlVsegZi1G7MtVGcBcMr6x2zLx3lK16t13bDLvkQDkdbUD_tAK-nRgSpz-NAVDtHy",
    ),
)

app.run()
app.wait_for_platforms()


print(app)

app.exit()