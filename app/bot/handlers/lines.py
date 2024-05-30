from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from httpx import HTTPStatusError

from bot.utils import get_user_handle
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


@lines_router.message(Command("lines"))
async def help_command_handler(message: Message):
    try:
        handle: str = get_user_handle(message)
    except ValueError as e:
        await message.reply(e.args[0])
        return
    targets: Iterable[Target] = await get_user_targets(user_handle=handle)
    for target in targets:
        day: datetime = datetime.now(timezone.utc) - timedelta(days=100)
        try:
            day_stats = await get_target_stats(
                repo=target.repo, committer=target.committer, since=day
            )
        except HTTPStatusError:
            await message.reply(
                f"Can't get info for <{target.repo} | {target.committer}>"
            )
            return
        await message.reply(
            f"For <{target.repo} | {target.committer}> = {str(format_simple_res(day_stats))}"
        )
