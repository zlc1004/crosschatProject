import crosschat
import discord
from typing import Optional
from rich import print

class DiscordPlatform(crosschat.Platform):
    """
    A platform implementation for Discord, integrating with the CrossChat framework.

    Attributes:
        crosschat (crosschat.CrossChat): The CrossChat instance managing this platform.
        name (str): The name of the platform, default is "discord".
        client (discord.Client): The Discord client instance.
        token (str): The bot token used to authenticate with Discord.
        thread (threading.Thread): The thread running the Discord client.
        running (bool): Indicates whether the platform is running.
    """

    def __init__(
        self, crosschat: crosschat.CrossChat, token: str, name: str = "discord"
    ):
        """
        Initializes the DiscordPlatform.

        Args:
            crosschat (crosschat.CrossChat): The CrossChat instance managing this platform.
            token (str): The bot token used to authenticate with Discord.
            name (str, optional): The name of the platform. Defaults to "discord".
        """
        super().__init__(crosschat=crosschat, name=name)
        self.name = name
        self.client = discord.Client(intents=discord.Intents.all())
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.token = token
        self.running = False
        self.add_to_crosschat()
        self.task = None

    async def on_ready(self):
        """
        Event handler triggered when the Discord client is ready.

        Prints the bot's username and sets the running status to True.
        """
        self.crosschat.logger.info(f"Logged in as {self.client.user}")
        self.running = True

    async def on_message(self, message: discord.Message):
        """
        Event handler triggered when a message is received on Discord.

        Args:
            message (discord.Message): The message object received from Discord.
        """
        # print(f"Received message: {message.content}")
        # Ignore messages from the bot itself
        if message.author == self.client.user:
            return

        # Get the corresponding channel in CrossChat
        channel = self.crosschat.get_channel(message.channel.id, self.name)
        # print(f"Channel: {channel}")
        if channel:
            # Get the corresponding user in CrossChat
            user = crosschat.User(message.author.display_name, message.author.name)
            attachments = [crosschat.Attachment(i.url) for i in message.attachments]
            # Create an original message and wrap it in a Message object
            original_msg = crosschat.OriginalMessage(
                self.crosschat,
                channel,
                user,
                message.content,
                message.id,
                self,
                attachments,
            )
            wrapped_msg = crosschat.Message(self.crosschat, original_msg)
            # Broadcast the message
            await wrapped_msg.broadcast()
            print(wrapped_msg)

    def make_webhook(self, id: int, token: str) -> None:
        """
        Creates a partial webhook object.

        Args:
            id (int): The webhook ID.
            token (str): The webhook token.

        Returns:
            discord.SyncWebhook: The created webhook object.
        """
        return discord.SyncWebhook.partial(id=id, token=token)

    async def send_message(
        self,
        channel: crosschat.Channel,
        content: str,
        user: crosschat.User = crosschat.User,
        reply: Optional[crosschat.OriginalMessage] = None,
        attachments: list[crosschat.Attachment] = [],
    ) -> int:
        """
        Sends a message to a Discord channel.

        Args:
            channel (crosschat.Channel): The target channel.
            content (str): The message content.
            user (crosschat.User, optional): The user sending the message. Defaults to crosschat.User.
            reply (Optional[crosschat.OriginalMessage], optional): The message being replied to. Defaults to None.
            attachments (list[crosschat.Attachment], optional): Attachments to include. Defaults to an empty list.

        Returns:
            int: The ID of the sent message, or 0 if the channel is not found.
        """
        # Send the message to the specified Discord channel
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            webhook: discord.Webhook = channel.get_extra_data("discord_webhook")
            if not webhook:
                self.crosschat.logger.error(f"Webhook not found in channel {channel}.")
                return 0
            message: discord.WebhookMessage = webhook.send(
                content=self.crosschat.make_reply_str(reply) + content,
                username=user.get_name(),
                avatar_url=user.get_profile_picture(),
                wait=1,
            )
            message_id = message.id
            for attachment in attachments:
                message.reply(
                    content=attachment.file_url,
                    username=user.get_name(),
                    avatar_url=user.get_profile_picture(),
                )
                self.crosschat.logger.info(
                    f"Uploaded attachment: '{attachment.file_url}' in channel {channel} on Discord."
                )
            self.crosschat.logger.info(
                f"Sent message: '{content}' in channel {channel} on Discord. ID: {message_id}"
            )
            return message_id  # Returning the message ID
        return 0  # In case the channel is not found

    async def edit_message(
        self, channel: crosschat.Channel, message: crosschat.Message, new_content: str
    ) -> None:
        """
        Edits a message in a Discord channel.

        Args:
            channel (crosschat.Channel): The target channel.
            message (crosschat.Message): The message to edit.
            new_content (str): The new content for the message.
        """
        # Get the message ID from CrossChat and edit the message on Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            webhook: discord.Webhook = channel.get_extra_data("discord_webhook")
            message: discord.WebhookMessage = webhook.edit_message(
                message_id=message.get_id(self.name), content=new_content
            )
            self.crosschat.logger.info(f"Edited message with ID {message.id} to: '{message.content}'")

    async def delete_message(
        self,
        channel: crosschat.Channel,
        message: crosschat.Message,
    ) -> None:
        """
        Deletes a message from a Discord channel.

        Args:
            channel (crosschat.Channel): The target channel.
            message (crosschat.Message): The message to delete.
        """
        # Get the message ID from CrossChat and delete the message on Discord
        discord_channel = self.client.get_channel(channel.get_id(self.name))
        if discord_channel:
            webhook: discord.Webhook = channel.get_extra_data("discord_webhook")
            webhook.delete_message(message.get_id(self.name))
            self.crosschat.logger.info(f"Deleted message with ID {message.get_id(self.name)}")

    async def get_message(
        self,
        channel: crosschat.Channel,
        message: crosschat.Message,
    ) -> Optional[crosschat.OriginalMessage]:
        """
        Retrieves a message from a Discord channel.

        Args:
            channel (crosschat.Channel): The target channel.
            message (crosschat.Message): The message to retrieve.

        Returns:
            Optional[crosschat.OriginalMessage]: The retrieved message, or None if not found.
        """
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

    async def run(self) -> None:
        """
        Starts the Discord client in a separate thread.
        """
        # discord.utils.setup_logging(
        #         handler=discord.utils.MISSING,
        #         formatter=discord.utils.MISSING,
        #         level=discord.utils.MISSING,
        #         root=False,
        #     )
        # Start the Discord client in a separate thread
        await self.client.start(self.token, reconnect=True)
    
    def health_check(self) -> bool:
        """
        Performs a health check to determine if the platform is running.

        Returns:
            bool: True if the platform is running, False otherwise.
        """
        return self.running and self.client.is_ready()

    async def exit(self):
        """
        Stops the Discord client and terminates the thread.
        """
        self.crosschat.logger.info("Stopping Discord client...")
        await self.client.close()
        self.crosschat.logger.info("Discord client stopped.")
        self.running = False
