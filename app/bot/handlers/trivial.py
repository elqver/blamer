from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Router


trivial_router = Router(name=__name__)


@trivial_router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer("""\
Hello!
I hope this bot will help you with productivity control!
The main idea is to be able to check 
how many lines of code you have published recently.
Be sure to check futher commands with:
/help

I will do my best to add smart dialogs later on 
with ChatGPT api
""")


@trivial_router.message(Command("help"))
async def help_command_handler(_: Message): ...
