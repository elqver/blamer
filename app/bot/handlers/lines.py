from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InaccessibleMessage,
)
from aiogram.types.message import Message
from httpx import HTTPStatusError

from github_api import get_target_stats
from models.target import Target, get_user_targets


lines_router = Router(name=__name__)


def format_simple_res(stats):
    res = {
        "total": 0,
        "additions": 0,
        "deletions": 0,
        "pure_additions": 0,
    }
    for s in stats:
        res["total"] += s["total"]
        res["additions"] += s["additions"]
        res["deletions"] += s["deletions"]
        res["pure_additions"] += max(0, s["additions"] - s["deletions"])
    return res


class TimePeriod(CallbackData, prefix="linestimeperiod"):
    days: int


@lines_router.message(Command("lines"))
async def help_command_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"For last {days} {'day' if days == 1 else 'days'}",
                    callback_data=TimePeriod(days=days).pack(),
                )
                for days in (1, 7, 30)
            ]
        ]
    )
    await message.answer("Select period to count your lines:", reply_markup=keyboard)


@lines_router.callback_query(TimePeriod.filter())
async def process_lines_for_period(
    callback_query: CallbackQuery, callback_data: TimePeriod
):
    handle = callback_query.from_user.username
    if handle is None:
        await callback_query.answer("Can't get user handle")
        raise ValueError("No user handle")
    if callback_query.message is None or callback_query.message is InaccessibleMessage:
        await callback_query.answer(
            f"Can't get message: {type(callback_query.message)}"
        )
        raise ValueError("Can't get message")
    all_stats = {
        "total": 0,
        "additions": 0,
        "deletions": 0,
        "pure_additions": 0,
    }
    targets: Iterable[Target] = await get_user_targets(user_handle=handle)
    for target in targets:
        day: datetime = datetime.now(timezone.utc) - timedelta(days=callback_data.days)
        try:
            day_stats = await get_target_stats(
                repo=target.repo, committer=target.committer, since=day
            )
        except HTTPStatusError:
            await callback_query.answer(
                f"Can't get info for <{target.repo} | {target.committer}>"
            )
            return
        simple_formated_day_stats = format_simple_res(day_stats)
        await callback_query.message.reply(  # type: ignore
            text=f"For <{target.repo} | {target.committer}> = {str(simple_formated_day_stats)}"
        )
        for key, value in simple_formated_day_stats.items():
            all_stats[key] += value
    await callback_query.message.reply(text=f"So in deletions: {str(all_stats)}")  # type: ignore
