import crosschat
from rich import print

cc = crosschat.CrossChat()

class DiscordPlatform(crosschat.Platform):
    def __init__(self, crosschat):
        super().__init__(crosschat)
        self.name = "discord"

class SlackPlatform(crosschat.Platform):
    def __init__(self, crosschat):
        super().__init__(crosschat)
        self.name = "slack"

class TelegramPlatform(crosschat.Platform):
    def __init__(self, crosschat):
        super().__init__(crosschat)
        self.name = "telegram"

class GoogleChatPlatform(crosschat.Platform):
    def __init__(self, crosschat):
        super().__init__(crosschat)
        self.name = "google_chat"
discord = DiscordPlatform(cc)
slack = SlackPlatform(cc)
telegram = TelegramPlatform(cc)
google_chat = GoogleChatPlatform(cc)
discord.add_to_crosschat()
slack.add_to_crosschat()
telegram.add_to_crosschat()
google_chat.add_to_crosschat()
# Step 3: Create and add channels
discord_channel = crosschat.Channel(cc, "general")
discord_channel.set_id("discord", 100)
discord_channel.set_id("slack", 200)
discord_channel.set_id("telegram", 300)
discord_channel.set_id("google_chat", 400)
cc.add_channel(discord_channel)
# Step 4: Create and add a user
user = crosschat.User("Alice", "alice123")
cc.add_user(user)
# Step 5: Create and add original message
original_msg = crosschat.OriginalMessage(cc, discord_channel, user, "Hello from Discord!", 123, discord)
# Step 6: Wrap message and broadcast
message = crosschat.Message(cc, original_msg)
cc.add_message(message)
print("Original Message:")
print(original_msg)
print(cc.get_platforms_str())
print("\nBroadcasting...")
message.broadcast()
print("\nFinal Message State:")
print(message)
print("\n Edit Message:")
message.edit("EDITED")
print("\n Final Message State after Edit:")
print(message)