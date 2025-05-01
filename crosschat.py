from typing import Union, Optional, Any
import random
import time
import asyncio
import threading

def override(func):
    """
    A decorator to indicate that a method should be overridden in a child class.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The original function.
    """
    return func


class CrossChat:
    """
    Manages communication across multiple platforms, channels, and users.

    Attributes:
        channels (list[Channel]): List of channels in the system.
        users (list[User]): List of users in the system.
        platforms (dict[str, Platform]): Dictionary of platform names to Platform objects.
        messages (list[Message]): List of messages in the system.
    """

    def __init__(self):
        """
        Initializes the CrossChat instance with empty lists and dictionaries for channels, users, platforms, and messages.
        """
        self.channels: list["Channel"] = []
        self.users: list["User"] = []
        self.platforms: dict[str, "Platform"] = {}
        self.messages: list["Message"] = []
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self.loop.run_forever,
            daemon=True
        )

    def add_platform(self, name: str, platform: "Platform") -> None:
        """
        Adds a platform to the CrossChat system.

        Args:
            name (str): The name of the platform.
            platform (Platform): The platform object to add.
        """
        self.platforms[name] = platform

    def get_platform(self, name: str) -> Optional["Platform"]:
        """
        Retrieves a platform by its name.

        Args:
            name (str): The name of the platform.

        Returns:
            Optional[Platform]: The platform object if found, otherwise None.
        """
        return self.platforms.get(name)

    def get_platforms_str(self) -> list[str]:
        """
        Retrieves a list of platform names.

        Returns:
            list[str]: List of platform names.
        """
        return list(self.platforms.keys())

    def add_channel(self, channel: "Channel") -> None:
        """
        Adds a channel to the CrossChat system.

        Args:
            channel (Channel): The channel object to add.
        """
        self.channels.append(channel)

    def add_user(self, user: "User") -> None:
        """
        Adds a user to the CrossChat system.

        Args:
            user (User): The user object to add.
        """
        self.users.append(user)

    def add_message(self, message: "Message") -> None:
        """
        Adds a message to the CrossChat system.

        Args:
            message (Message): The message object to add.
        """
        self.messages.append(message)

    def get_channel(
        self, id: int, platform: Union[str, "Platform"]
    ) -> Optional["Channel"]:
        """
        Retrieves a channel by its ID and platform.

        Args:
            id (int): The ID of the channel.
            platform (Union[str, Platform]): The platform name or object.

        Returns:
            Optional[Channel]: The channel object if found, otherwise None.
        """
        key = platform if isinstance(platform, str) else platform.name
        for channel in self.channels:
            if channel.get_id(key) == id:
                return channel
        return None

    def make_reply_str(self, reply: Optional["OriginalMessage"]) -> str:
        """
        Generates a reply string for a given message.

        Args:
            reply (Optional[OriginalMessage]): The original message being replied to.

        Returns:
            str: The formatted reply string.
        """
        if reply:
            content = reply.content
            if len(reply.content) > 100:
                content = reply.content[:70] + "..." + reply.content[-20:]
            return f"Replying to {reply.user.get_name()}: '{content}'\n"
        return ""

    def __repr__(self) -> str:
        """
        Returns a string representation of the CrossChat instance.

        Returns:
            str: String representation of the CrossChat instance.
        """
        return (
            f"CrossChat(channels={self.channels}, users={self.users}, "
            f"messages={self.messages}, platforms={self.platforms})"
        )

    def wait_for_platforms(self) -> None:
        """
        Waits for all platforms to pass their health checks.
        """
        for platform in self.platforms.values():
            while not platform.health_check():
                print(f"Waiting for platform {platform.name} to be healthy...")
                time.sleep(1)
        print("All platforms are healthy!")

    def run(self) -> None:
        """
        Starts all platforms and runs the CrossChat system.
        """
        for platform in self.platforms.values():
            platform.run()
        print("Running CrossChat and all platforms...")
        self.thread.start()
        

    def exit(self) -> None:
        """
        Exits all platforms and shuts down the CrossChat system.
        """
        for platform in self.platforms.values():
            platform.exit()
        print("Exiting CrossChat and closing all platforms...")

    def wait_for_task(self, task: asyncio.Task) -> None:
        """
        Waits for a specific task to complete.

        Args:
            task (asyncio.Task): The task to wait for.
        """
        while not task.done():
            time.sleep(0.1)

class Platform:
    """
    Represents a communication platform in the CrossChat system.

    Attributes:
        name (str): The name of the platform.
        crosschat (CrossChat): The CrossChat instance managing the platform.
    """

    @override
    def __init__(self, crosschat: CrossChat, name: str = "name"):
        """
        Initializes the Platform instance.

        Args:
            crosschat (CrossChat): The CrossChat instance managing the platform.
            name (str): The name of the platform.
        """
        self.name: str = name
        self.crosschat = crosschat

    def add_to_crosschat(self) -> None:
        """
        Adds the platform to the CrossChat system.
        """
        self.crosschat.add_platform(self.name, self)

    @override
    def edit_message(
        self, channel: "Channel", message: "Message", newContent: str
    ) -> None:
        """
        Edits a message on the platform.

        Args:
            channel (Channel): The channel where the message is located.
            message (Message): The message to edit.
            newContent (str): The new content for the message.
        """
        messageId = message.get_id(self.name)
        channelId = channel.get_id(self.name)
        print(
            f"Editing message {messageId} in channel {channelId} on platform {self.name} to {newContent}"
        )

    @override
    def delete_message(self, channel: "Channel", message: "Message") -> None:
        """
        Deletes a message from the platform.

        Args:
            channel (Channel): The channel where the message is located.
            message (Message): The message to delete.
        """
        messageId = message.get_id(self.name)
        channelId = channel.get_id(self.name)
        print(
            f"Deleting message {messageId} in channel {channelId} on platform {self.name}"
        )

    @override
    def send_message(
        self,
        channel: "Channel",
        content: str,
        user: "User",
        reply: Optional["OriginalMessage"] = None,
        attachments: list["Attachment"] = [],
    ) -> int:
        """
        Sends a message on the platform.

        Args:
            channel (Channel): The channel where the message will be sent.
            content (str): The content of the message.
            user (User): The user sending the message.
            reply (Optional[OriginalMessage]): The message being replied to, if any.

        Returns:
            int: The ID of the sent message.
        """
        channelId = channel.get_id(self.name)
        print(
            f"Sending message in channel {channelId} on platform {self.name} "
            f"with content '{content}' by {user.name}"
        )
        if reply:
            replyId = reply.get_id(self.name)
            print(
                f"Replying to message {replyId} on platform {reply.platform.name} from {reply.user.get_name()} with content '{reply.content}'"
            )
        if attachments:
            for attachment in attachments:
                print(f"Sending attachment: {attachment.file_url}")
        return random.randint(100000, 999999)  # Simulated message ID

    @override
    def get_message(self, channel: "Channel", message: "Message") -> None:
        """
        Retrieves a message from the platform.

        Args:
            channel (Channel): The channel where the message is located.
            message (Message): The message to retrieve.
        """
        messageId = message.get_id(self.name)
        channelId = channel.get_id(self.name)
        print(
            f"Getting message {messageId} in channel {channelId} on platform {self.name}"
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the Platform instance.

        Returns:
            str: String representation of the Platform instance.
        """
        return f"Platform(name={self.name})"

    @override
    def run(self) -> None:
        """
        Starts the platform.
        """
        print(f"Running platform {self.name}...")
        pass

    @override
    def exit(self) -> None:
        """
        Exits the platform and performs cleanup.
        """
        print(f"Exiting platform {self.name}...")
        pass

    @override
    def health_check(self) -> bool:
        """
        Performs a health check for the platform.

        Returns:
            bool: True if the platform is healthy, otherwise False.
        """
        print(f"Performing health check for platform {self.name}...")
        return True


class Channel:
    """
    Represents a communication channel in the CrossChat system.

    Attributes:
        name (str): The name of the channel.
        ids (dict[str, int]): A dictionary mapping platform names to their respective channel IDs.
        crosschat (CrossChat): The CrossChat instance managing the channel.
        extra_data (dict[str, str]): Additional metadata for the channel.
    """

    def __init__(self, crosschat: CrossChat, name: str):
        """
        Initializes the Channel instance.

        Args:
            crosschat (CrossChat): The CrossChat instance managing the channel.
            name (str): The name of the channel.
        """
        self.name = name
        self.ids: dict[str, int] = {}
        self.crosschat = crosschat
        self.extra_data: dict[str, str] = {}

    def get_id(self, platform: Union[str, "Platform"]) -> Optional[int]:
        """
        Retrieves the channel ID for a specific platform.

        Args:
            platform (Union[str, Platform]): The platform name or object.

        Returns:
            Optional[int]: The channel ID if found, otherwise None.
        """
        key = platform if isinstance(platform, str) else platform.name
        return self.ids.get(key)

    def set_id(self, platform: Union[str, "Platform"], id: int) -> None:
        """
        Sets the channel ID for a specific platform.

        Args:
            platform (Union[str, Platform]): The platform name or object.
            id (int): The channel ID to set.
        """
        key = platform if isinstance(platform, str) else platform.name
        self.ids[key] = id

    def set_extra_data(self, key: str, value: Any) -> None:
        """
        Sets additional metadata for the channel.

        Args:
            key (str): The metadata key.
            value (Any): The metadata value.
        """
        self.extra_data[key] = value

    def get_extra_data(self, key: str) -> Optional[Any]:
        """
        Retrieves additional metadata for the channel.

        Args:
            key (str): The metadata key.

        Returns:
            Optional[Any]: The metadata value if found, otherwise None.
        """
        return self.extra_data.get(key, None)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Channel instance.

        Returns:
            str: String representation of the Channel instance.
        """
        return f"Channel(name={self.name}, ids={self.ids})"

    def get_message(
        self, platform: Union[str, "Platform"], id: int
    ) -> Optional["Message"]:
        """
        Retrieves a message from the channel by its ID and platform.

        Args:
            platform (Union[str, Platform]): The platform name or object.
            id (int): The message ID.

        Returns:
            Optional[Message]: The message object if found, otherwise None.
        """
        platform_obj = (
            self.crosschat.get_platform(platform)
            if isinstance(platform, str)
            else platform
        )
        if platform_obj is None:
            return None
        return platform_obj.get_message(self, id)


class User:
    """
    Represents a user in the CrossChat system.

    Attributes:
        display_name (str): The display name of the user.
        username (str): The username of the user.
        name (str): The full name of the user in the format "display_name(@username)".
        profile_picture (str): The URL of the user's profile picture.
    """

    def __init__(self, display_name: str, username: str, profile_picture: str = None):
        """
        Initializes the User instance.

        Args:
            display_name (str): The display name of the user.
            username (str): The username of the user.
            profile_picture (str, optional): The URL of the user's profile picture. Defaults to None.
        """
        self.display_name = display_name
        self.username = username
        self.name = f"{display_name}(@{username})"
        self.profile_picture = profile_picture

    def get_profile_picture(self) -> str:
        """
        Retrieves the user's profile picture URL.

        Returns:
            str: The URL of the user's profile picture, or a default image URL if not set.
        """
        return (
            self.profile_picture
            if self.profile_picture
            else "https://i.pinimg.com/474x/25/1c/e1/251ce139d8c07cbcc9daeca832851719.jpg"
        )

    def get_name(self) -> str:
        """
        Retrieves the full name of the user.

        Returns:
            str: The full name of the user in the format "display_name(@username)".
        """
        return f"{self.display_name}(@{self.username})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the User instance.

        Returns:
            str: String representation of the User instance.
        """
        return f"User(display_name={self.display_name}, username={self.username})"

class Attachment:
    """
    Represents an attachment in the CrossChat system.
    Attributes:
        file_url (str): The URL of the file attachment.
    """
    def __init__(self, file_url: str):
        """
        Initializes the Attachment instance.

        Args:
            file_url (str): The URL of the file attachment.
        """
        self.file_url = file_url
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Attachment instance.

        Returns:
            str: String representation of the Attachment instance.
        """
        return f"Attachment(file_url={self.file_url})"

class OriginalMessage:
    """
    Represents an original message in the CrossChat system.

    Attributes:
        content (str): The content of the message.
        id (int): The unique identifier of the message.
        platform (Platform): The platform where the message was sent.
        user (User): The user who sent the message.
        channel (Channel): The channel where the message was sent.
        crosschat (CrossChat): The CrossChat instance managing the message.
    """

    def __init__(
        self,
        crosschat: CrossChat,
        channel: Channel,
        user: User,
        content: str,
        id: int,
        platform: Platform,
        attachments: list[Attachment] = [],
    ):
        """
        Initializes the OriginalMessage instance.

        Args:
            crosschat (CrossChat): The CrossChat instance managing the message.
            channel (Channel): The channel where the message was sent.
            user (User): The user who sent the message.
            content (str): The content of the message.
            id (int): The unique identifier of the message.
            platform (Platform): The platform where the message was sent.
        """
        self.content = content
        self.id = id
        self.platform = platform
        self.user = user
        self.channel = channel
        self.crosschat = crosschat
        self.attachments = attachments

    def __repr__(self) -> str:
        """
        Returns a string representation of the OriginalMessage instance.

        Returns:
            str: String representation of the OriginalMessage instance.
        """
        return (
            f"OriginalMessage(content={self.content}, id={self.id}, "
            f"platform={self.platform.name}, user={self.user.name}, "
            f"channel={self.channel.name})"
        )


class Message:
    """
    Represents a message in the CrossChat system, which can be broadcasted, edited, or deleted
    across multiple platforms.

    Attributes:
        channel (Channel): The channel where the message was sent.
        user (User): The user who sent the message.
        content (str): The content of the message.
        ids (dict[str, int]): A dictionary mapping platform names to their respective message IDs.
        originalMessage (OriginalMessage): The original message object.
        crosschat (CrossChat): The CrossChat instance managing the message.
        reply (Optional[OriginalMessage]): The message being replied to, if any.
    """

    def __init__(
        self,
        crosschat: CrossChat,
        originalMessage: OriginalMessage,
        reply: Optional[OriginalMessage] = None,
    ):
        """
        Initializes the Message instance.

        Args:
            crosschat (CrossChat): The CrossChat instance managing the message.
            originalMessage (OriginalMessage): The original message object.
            reply (Optional[OriginalMessage], optional): The message being replied to, if any. Defaults to None.
        """
        self.channel = originalMessage.channel
        self.user = originalMessage.user
        self.content = originalMessage.content
        self.ids: dict[str, int] = {}
        self.originalMessage = originalMessage
        self.crosschat = crosschat
        self.ids[originalMessage.platform.name] = originalMessage.id
        self.reply = reply

    def get_id(self, platform: Union[str, Platform]) -> Optional[int]:
        """
        Retrieves the message ID for a specific platform.

        Args:
            platform (Union[str, Platform]): The platform name or object.

        Returns:
            Optional[int]: The message ID if found, otherwise None.
        """
        key = platform if isinstance(platform, str) else platform.name
        return self.ids.get(key)

    def set_id(self, platform: Union[str, Platform], id: int) -> None:
        """
        Sets the message ID for a specific platform.

        Args:
            platform (Union[str, Platform]): The platform name or object.
            id (int): The message ID to set.
        """
        key = platform if isinstance(platform, str) else platform.name
        self.ids[key] = id

    def broadcast(self) -> None:
        """
        Broadcasts the message to all platforms except the one it originated from.
        """
        originalPlatformName = self.originalMessage.platform.name
        platforms = self.crosschat.get_platforms_str()

        if originalPlatformName in platforms:
            platforms.remove(originalPlatformName)

        for platformName in platforms:
            platform = self.crosschat.get_platform(platformName)
            if platform is not None:
                returnedId = platform.send_message(
                    self.channel, self.content, self.user, self.reply
                )
                self.set_id(platform.name, returnedId)

    def edit(self, newContent: str) -> None:
        """
        Edits the message content across all platforms.

        Args:
            newContent (str): The new content for the message.
        """
        platforms = self.crosschat.platforms.values()
        for platform in platforms:
            platform.edit_message(self.channel, self, newContent)
        self.content = newContent

    def delete(self) -> None:
        """
        Deletes the message from all platforms.
        """
        platforms = self.crosschat.platforms.values()
        for platform in platforms:
            platform.delete_message(self.channel, self)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Message instance.

        Returns:
            str: String representation of the Message instance.
        """
        return (
            f"Message(channel={self.channel}, user={self.user}, "
            f"content={self.content}, ids={self.ids}), "
            f"OriginalMessage={self.originalMessage}"
        )


def main():
    cc = CrossChat()

    class DiscordPlatform(Platform):
        def __init__(self, crosschat):
            super().__init__(crosschat)
            self.name = "discord"

    class SlackPlatform(Platform):
        def __init__(self, crosschat):
            super().__init__(crosschat)
            self.name = "slack"

    class TelegramPlatform(Platform):
        def __init__(self, crosschat):
            super().__init__(crosschat)
            self.name = "telegram"

    class GoogleChatPlatform(Platform):
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
    cc.run()
    cc.wait_for_platforms()
    discord_channel = Channel(cc, "general")
    discord_channel.set_id("discord", 100)
    discord_channel.set_id("slack", 200)
    discord_channel.set_id("telegram", 300)
    discord_channel.set_id("google_chat", 400)
    cc.add_channel(discord_channel)
    user = User("Alice", "alice123")
    cc.add_user(user)
    original_msg = OriginalMessage(
        cc, discord_channel, user, "Hello from Discord!", 123, discord
    )
    message = Message(cc, original_msg)
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
    cc.exit()


if __name__ == "__main__":
    main()