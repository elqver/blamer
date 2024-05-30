from aiogram.types import Message


def get_user_handle(message: Message) -> str:
    if message.from_user is None or message.from_user.username is None:
        error_line = "can't set up target without user: message without user"
        raise ValueError(error_line)
    return message.from_user.username
