import crosschat
import discordPlatform
import telegramPlatform

with open("./tokens/discord", "r") as f:
    discordBotToken = f.read().strip()
with open("./tokens/tg", "r") as f:
    telegramBotToken = f.read().strip()

app = crosschat.CrossChat()
discord = discordPlatform.DiscordPlatform(app, discordBotToken)
telegram = telegramPlatform.TelegramPlatform(app, telegramBotToken)
platform = crosschat.Platform(app, "test")
platform.add_to_crosschat()

channel = crosschat.Channel(app, "general")

channel.set_id("discord", 1367251777606385777)
channel.set_id("telegram", -4677825942)
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

message = crosschat.OriginalMessage(
    app,
    channel,
    crosschat.User("kobosh", "koboshusername"),
    "Hello world",
    123456789,
    platform,
)

wrapped_message = crosschat.Message(app,message)

wrapped_message.broadcast()

app.exit()