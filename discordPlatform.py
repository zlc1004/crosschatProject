import crosschat
import discord
from typing import Union, Optional
import threading

class DiscordPlatform(crosschat.Platform):
    def __init__(self, crosschat: crosschat.CrossChat, token: str):
        super().__init__(crosschat)
        self.name = "discord"
        self.client = discord.Client(intents=discord.Intents.default())
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.token = token
        self.thread = threading.Thread(target=self.client.run, args=(self.token,), daemon=True)

    def on_ready(self):
        print(f"Logged in as {self.client.user}")

    def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author == self.client.user:
            return

        # Get the corresponding channel in CrossChat
        channel = self.crosschat.get_channel(message.channel.id, self.name)
        if channel:
            # Get the corresponding user in CrossChat
            user = self.crosschat.get_user(message.author.id, self.name)
            # Create an original message and wrap it in a Message object
            original_msg = crosschat.OriginalMessage(
                self.crosschat, channel, user, message.content, message.id, self
            )
            wrapped_msg = crosschat.Message(self.crosschat, original_msg)
            # Broadcast the message
            wrapped_msg.broadcast()

    def send_message(self, channel: "crosschat.Channel", content: str, user: "crosschat.User") -> int:
        # Send the message to the specified Discord channel
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            message = discord_channel.send(content)
            print(f"Sent message: '{content}' in channel {discord_channel.name} on Discord.")
            return message.id  # Returning the message ID
        return 0  # In case the channel is not found

    def edit_message(self, channel: "crosschat.Channel", message: "crosschat.Message", new_content: str) -> None:
        # Get the message ID from CrossChat and edit the message on Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            discord_message = discord_channel.get_partial_message(message.get_id(self.name))
            discord_message.edit(content=new_content)
            print(f"Edited message with ID {discord_message.id} to: '{new_content}'")

    def delete_message(self, channel: "crosschat.Channel", message: "crosschat.Message") -> None:
        # Get the message ID from CrossChat and delete the message on Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            discord_message = discord_channel.get_partial_message(message.get_id(self.name))
            discord_message.delete()
            print(f"Deleted message with ID {discord_message.id}")

    def get_message(self, channel: "crosschat.Channel", message: "crosschat.Message") -> Optional[discord.Message]:
        # Get the message ID from CrossChat and retrieve the message from Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            discord_message = discord_channel.fetch_message(message.get_id(self.name))
            print(f"Fetched message with ID {discord_message.id}")
            return discord_message
        return None  # If the channel or message is not found

    def run(self):
        # Start the Discord client in a separate thread
        self.thread.start()
