import os.path
from datetime import datetime

from dotenv import load_dotenv
import asyncio

import aiogram


from github_api import get_user_total_lines_delta

if os.path.exists('tg_creds.env'):
    load_dotenv('tg_creds.env')


TG_TOKEN = os.getenv('TG_TOKEN')

dp = aiogram.Dispatcher()


@dp.message(aiogram.filters.CommandStart())
async def start(message: aiogram.types.Message):
    await message.answer('Hello, I am a bot!')


# get current line progress endpoint
@dp.message(aiogram.filters.Command("lines"))
async def get_lines(message: aiogram.types.Message):
    await message.answer('Fetching current line progress...')
    user = message.from_user.username
    today = datetime.now().strftime('%Y-%m-%dT00:00:00Z')
    result = await get_user_total_lines_delta(user, today)
    await message.answer(f'User {user} has added {result} lines of code today')


async def main():
    bot = aiogram.Bot(token=TG_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
