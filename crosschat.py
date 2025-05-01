from typing import Union, Optional, Any
import random

class CrossChat:
    """
    A class to manage cross-platform chat functionalities, including channels, users, 
    platforms, and messages.
    Attributes:
        channels (list[Channel]): A list of channels associated with the chat system.
        users (list[User]): A list of users participating in the chat system.
        platforms (dict[str, Platform]): A dictionary mapping platform names to their 
            respective Platform objects.
    Methods:
        add_platform(name: str, platform: Platform) -> None:
            Adds a platform to the chat system.
        get_platform(name: str) -> Optional[Platform]:
            Retrieves a platform by its name.
        get_platforms_str() -> list[str]:
            Returns a list of platform names as strings.
        add_channel(channel: Channel) -> None:
            Adds a channel to the chat system.
        add_user(user: User) -> None:
            Adds a user to the chat system.
        add_message(message: Message) -> None:
            Adds a message to the chat system.
        get_channel(id: int, platform: Union[str, Platform]) -> Optional[Channel]:
            Retrieves a channel by its ID and platform.
        __repr__() -> str:
            Returns a string representation of the CrossChat object.
    """
    def __init__(self):
        self.channels: list["Channel"] = []
        self.users: list["User"] = []
        self.platforms: dict[str, "Platform"] = {}

    def add_platform(self, name: str, platform: "Platform") -> None:
        self.platforms[name] = platform

    def get_platform(self, name: str) -> Optional["Platform"]:
        return self.platforms.get(name)

    def get_platforms_str(self) -> list[str]:
        return list(self.platforms.keys())

    def add_channel(self, channel: "Channel") -> None:
        self.channels.append(channel)

    def add_user(self, user: "User") -> None:
        self.users.append(user)

    def add_message(self, message: "Message") -> None:
        self.messages.append(message)

    def get_channel(
        self, id: int, platform: Union[str, "Platform"]
    ) -> Optional["Channel"]:
        key = platform if isinstance(platform, str) else platform.name
        for channel in self.channels:
            if channel.get_id(key) == id:
                return channel
        return None

    def __repr__(self) -> str:
        return (
            f"CrossChat(channels={self.channels}, users={self.users}, "
            f"messages={self.messages}, platforms={self.platforms})"
        )


class Platform:
    """
    Represents a platform in the CrossChat system.
    This class provides methods to interact with a specific platform, including
    sending, editing, deleting, and retrieving messages, as well as performing
    platform-specific operations.
    Attributes:
        name (str): The name of the platform.
        crosschat (CrossChat): The CrossChat instance associated with the platform.
    Methods:
        add_to_crosschat() -> None:
            Adds the platform to the CrossChat instance.
        edit_message(channel: "Channel", message: "Message", newContent: str) -> None:
            Edits a message in a specified channel on the platform.
        delete_message(channel: "Channel", message: "Message") -> None:
            Deletes a message in a specified channel on the platform.
        send_message(channel: "Channel", content: str, user: "User") -> int:
            Sends a message to a specified channel on the platform.
            Returns a simulated message ID.
        get_message(channel: "Channel", message: "Message") -> None:
            Retrieves a message from a specified channel on the platform.
        run() -> None:
            Simulates running the platform, such as connecting to an API.
        health_check() -> bool:
            Performs a health check for the platform.
            Returns True if the platform is healthy.
        __repr__() -> str:
            Returns a string representation of the Platform instance.
    """
    def __init__(self, crosschat: CrossChat):
        self.name: str = "name"
        self.crosschat = crosschat
        
    def add_to_crosschat(self) -> None:
        self.crosschat.add_platform(self.name, self)

    def edit_message(self, channel: "Channel", message: "Message", newContent: str) -> None:
        messageId = message.get_id(self.name)
        channelId = channel.get_id(self.name)
        print(
            f"Editing message {messageId} in channel {channelId} on platform {self.name} to {newContent}"
        )

    def delete_message(self, channel: "Channel", message: "Message") -> None:
        messageId = message.get_id(self.name)
        channelId = channel.get_id(self.name)
        print(
            f"Deleting message {messageId} in channel {channelId} on platform {self.name}"
        )

    def send_message(self, channel: "Channel", content: str, user: "User") -> int:
        channelId = channel.get_id(self.name)
        print(
            f"Sending message in channel {channelId} on platform {self.name} "
            f"with content '{content}' by {user.name}"
        )
        return random.randint(100000,999999)  # Simulated message ID

    def get_message(self, channel: "Channel", message: "Message") -> None:
        messageId = message.get_id(self.name)
        channelId = channel.get_id(self.name)
        print(
            f"Getting message {messageId} in channel {channelId} on platform {self.name}"
        )

    def __repr__(self) -> str:
        return f"Platform(name={self.name})"
    
    def run(self) -> None:
        print(f"Running platform {self.name}...")
        # Simulate some platform-specific behavior
        # For example, connecting to an API, etc.
        pass
        # Simulate some platform-specific behavior
    
    def health_check(self) -> bool:
        # Simulate a health check for the platform
        print(f"Performing health check for platform {self.name}...")
        return True


class Channel:
    """
    Represents a communication channel within the CrossChat system.
    Attributes:
        name (str): The name of the channel.
        ids (dict[str, int]): A mapping of platform names to their respective IDs for this channel.
        crosschat (CrossChat): The CrossChat instance this channel belongs to.
        extra_data (dict[str, str]): A dictionary for storing additional metadata about the channel.
    Methods:
        __init__(crosschat: CrossChat, name: str):
            Initializes a Channel instance with the given CrossChat instance and name.
        get_id(platform: Union[str, "Platform"]) -> Optional[int]:
            Retrieves the ID associated with the given platform for this channel.
        set_id(platform: Union[str, "Platform"], id: int) -> None:
            Sets the ID for the given platform in this channel.
        set_extra_data(key: str, value: Any) -> None:
            Stores additional metadata for the channel using a key-value pair.
        get_extra_data(key: str) -> Optional[Any]:
            Retrieves the value of additional metadata for the given key.
        __repr__() -> str:
            Returns a string representation of the Channel instance.
        get_message(platform: Union[str, "Platform"], id: int) -> Optional["Message"]:
            Retrieves a message from the specified platform and ID for this channel.
    """
    def __init__(self, crosschat: CrossChat, name: str):
        self.name = name
        self.ids: dict[str, int] = {}
        self.crosschat = crosschat
        self.extra_data: dict[str, str] = {}

    def get_id(self, platform: Union[str, "Platform"]) -> Optional[int]:
        key = platform if isinstance(platform, str) else platform.name
        return self.ids.get(key)

    def set_id(self, platform: Union[str, "Platform"], id: int) -> None:
        key = platform if isinstance(platform, str) else platform.name
        self.ids[key] = id

    def set_extra_data(self, key: str, value: Any) -> None:
        self.extra_data[key] = value
    
    def get_extra_data(self, key: str) -> Optional[Any]:
        return self.extra_data.get(key, None)

    def __repr__(self) -> str:
        return f"Channel(name={self.name}, ids={self.ids})"

    def get_message(self, platform: Union[str, "Platform"], id: int) -> Optional["Message"]:
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
    A class representing a user with a display name, username, and optional profile picture.
    Attributes:
        display_name (str): The display name of the user.
        username (str): The unique username of the user.
        profile_picture (str, optional): The URL of the user's profile picture. Defaults to None.
    Methods:
        get_profile_picture() -> str:
            Returns the URL of the user's profile picture. If no profile picture is provided,
            returns a default placeholder image URL.
        get_name() -> str:
            Returns the user's name in the format "display_name(@username)".
        __repr__() -> str:
            Returns a string representation of the User object.
    """
    def __init__(self, display_name: str, username: str, profile_picture: str = None):
        self.display_name = display_name
        self.username = username
        self.name = f"{display_name}(@{username})"
        self.profile_picture = profile_picture
    
    def get_profile_picture(self) -> str:
        return self.profile_picture if self.profile_picture else "https://i.pinimg.com/474x/25/1c/e1/251ce139d8c07cbcc9daeca832851719.jpg"
    
    def get_name(self) -> str:
        return f"{self.display_name}(@{self.username})"
    
    def __repr__(self) -> str:
        return f"User(display_name={self.display_name}, username={self.username})"

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
    Methods:
        __repr__() -> str:
            Returns a string representation of the OriginalMessage instance.
    """
    def __init__(
        self,
        crosschat: CrossChat,
        channel: Channel,
        user: User,
        content: str,
        id: int,
        platform: Platform,
    ):
        self.content = content
        self.id = id
        self.platform = platform
        self.user = user
        self.channel = channel
        self.crosschat = crosschat

    def __repr__(self) -> str:
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
        channel (str): The channel where the message was sent.
        user (str): The user who sent the message.
        content (str): The content of the message.
        ids (dict[str, int]): A dictionary mapping platform names to their respective message IDs.
        originalMessage (OriginalMessage): The original message object.
        crosschat (CrossChat): The CrossChat instance managing the message.
    Methods:
        get_id(platform: Union[str, Platform]) -> Optional[int]:
            Retrieves the message ID for a specific platform.
        set_id(platform: Union[str, Platform], id: int) -> None:
            Sets the message ID for a specific platform.
        broadcast() -> None:
            Broadcasts the message to all platforms except the one it originated from.
        edit(newContent: str) -> None:
            Edits the message content across all platforms.
        delete() -> None:
            Deletes the message from all platforms.
        __repr__() -> str:
            Returns a string representation of the Message object.
    """
    def __init__(self, crosschat: CrossChat, originalMessage: OriginalMessage):
        self.channel = originalMessage.channel
        self.user = originalMessage.user
        self.content = originalMessage.content
        self.ids: dict[str, int] = {}
        self.originalMessage = originalMessage
        self.crosschat = crosschat
        self.ids[originalMessage.platform.name] = originalMessage.id

    def get_id(self, platform: Union[str, Platform]) -> Optional[int]:
        key = platform if isinstance(platform, str) else platform.name
        return self.ids.get(key)

    def set_id(self, platform: Union[str, Platform], id: int) -> None:
        key = platform if isinstance(platform, str) else platform.name
        self.ids[key] = id

    def broadcast(self) -> None:
        originalPlatformName = self.originalMessage.platform.name
        platforms = self.crosschat.get_platforms_str()
        
        # Remove the platform from the list that originally sent the message
        if originalPlatformName in platforms:
            platforms.remove(originalPlatformName)
        
        # Send the message to all other platforms
        for platformName in platforms:
            platform = self.crosschat.get_platform(platformName)
            if platform is not None:
                returnedId = platform.send_message(
                    self.channel,
                    self.content,
                    self.user,
                )
                self.set_id(platform.name, returnedId)

    def edit(self, newContent: str) -> None:
        platforms = self.crosschat.platforms.values()
        for platform in platforms:
            platform.edit_message(self.channel, self, newContent)
        self.content = newContent
        
    def delete(self) -> None:
        platforms = self.crosschat.platforms.values()
        for platform in platforms:
            platform.delete_message(self.channel, self)

    def __repr__(self) -> str:
        return (
            f"Message(channel={self.channel}, user={self.user}, "
            f"content={self.content}, ids={self.ids}), "
            f"OriginalMessage={self.originalMessage}"
        )
