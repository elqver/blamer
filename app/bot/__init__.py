import os
from aiogram import Bot, Dispatcher
from bot.handlers import trivial_router
from bot.handlers import targets_router
from bot.handlers import lines_router

TG_TOKEN = os.getenv("TG_TOKEN")
if TG_TOKEN is None:
    raise ValueError("no env for TG_TOKEN provided")


bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

dp.include_routers(
    trivial_router,
    targets_router,
    lines_router,
)
