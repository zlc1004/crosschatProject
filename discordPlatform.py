import crosschat
import discord
from typing import Union, Optional
import threading
import asyncio


class DiscordPlatform(crosschat.Platform):
    def __init__(self, crosschat: crosschat.CrossChat, token: str):
        super().__init__(crosschat)
        self.name = "discord"
        self.client = discord.Client(intents=discord.Intents.all())
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.token = token
        self.thread = threading.Thread(
            target=self.client.run, args=(self.token,), daemon=True
        )
        self.running = False
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "content-type": "application/json",
        }

    async def on_ready(self):
        print(f"Logged in as {self.client.user}")
        self.running = True

    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author == self.client.user:
            return

        # Get the corresponding channel in CrossChat
        channel = self.crosschat.get_channel(message.channel.id, self.name)
        if channel:
            # Get the corresponding user in CrossChat
            user = crosschat.User(message.author.display_name, message.author.name)
            # Create an original message and wrap it in a Message object
            original_msg = crosschat.OriginalMessage(
                self.crosschat, channel, user, message.content, message.id, self
            )
            wrapped_msg = crosschat.Message(self.crosschat, original_msg)
            # Broadcast the message
            wrapped_msg.broadcast()

    def make_webhook(self, id: int, token: str) -> None:
        return discord.SyncWebhook.partial(id=id, token=token)

    def send_message(
        self,
        channel: crosschat.Channel,
        content: str,
        user: crosschat.User = crosschat.User,
    ) -> int:
        # Send the message to the specified Discord channel
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            webhook: discord.Webhook = channel.get_extra_data("discord_webhook")
            message: discord.WebhookMessage = webhook.send(
                content=content,
                username=user.get_name(),
                avatar_url=user.get_profile_picture(),
                wait=1,
            )
            message_id = message.id
            print(
                f"Sent message: '{content}' in channel {channel} on Discord. ID: {message_id}"
            )
            return message_id  # Returning the message ID
        return 0  # In case the channel is not found

    def edit_message(
        self,
        channel: crosschat.Channel,
        message: Union[crosschat.Message, crosschat.OriginalMessage],
        new_content: str,
    ) -> None:
        # Get the message ID from CrossChat and edit the message on Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            webhook: discord.Webhook = channel.get_extra_data("discord_webhook")
            message:discord.WebhookMessage = webhook.edit_message(
                message_id=message.get_id(self.name),
                content=new_content
            )
            print(f"Edited message with ID {message.id} to: '{message.content}'")

    def delete_message(
        self,
        channel: crosschat.Channel,
        message: Union[crosschat.Message, crosschat.OriginalMessage],
    ) -> None:
        # Get the message ID from CrossChat and delete the message on Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            webhook: discord.Webhook = channel.get_extra_data("discord_webhook")
            webhook.delete_message(
                message.get_id(self.name)
            )
            print(f"Deleted message with ID {message.get_id(self.name)}")

    def get_message(
        self,
        channel: crosschat.Channel,
        message: Union[crosschat.Message, crosschat.OriginalMessage],
    ) -> Optional[crosschat.OriginalMessage]:
        # Get the message ID from CrossChat and retrieve the message from Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            discord_message = discord_channel.fetch_message(message.get_id(self.name))
            print(f"Fetched message with ID {discord_message.id}")
            wrapped_user = crosschat.User(
                discord_message.author.de, discord_message.author.id
            )
            wrapped_msg = crosschat.OriginalMessage(
                self.crosschat,
                channel,
                message.user,
                discord_message.content,
                discord_message.id,
                self,
            )
            return wrapped_msg
        return None

    def upload_attachment(self, channel: crosschat.Channel, file_path: str) -> None:
        # Upload an attachment to the specified Discord channel
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            with open(file_path, "rb") as f:
                discord_channel.send(file=discord.File(f))
                print(
                    f"Uploaded attachment: '{file_path}' in channel {discord_channel.name} on Discord."
                )

    def run(self) -> None:
        # Start the Discord client in a separate thread
        self.thread.start()

    def health_check(self) -> bool:
        return self.running
