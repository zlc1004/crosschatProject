from typing import Union, Optional, Any
import random

class CrossChat:
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
