import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from httpx import HTTPStatusError
from loguru import logger
from sqlalchemy.exc import IntegrityError

from github_api import check_repo_accessable
from bot.utils import get_user_handle
from models.base import async_session
from models.target import create_target, get_user_targets
from models.target import remove_target as remove_target_from_db


targets_router = Router(name=__name__)


class Target(StatesGroup):
    repo = State()
    committer = State()


@targets_router.message(Command("add"))
async def add_repo_user(message: Message, state: FSMContext) -> None:
    await state.set_state(Target.repo)
    await message.answer("What is target repo?")


@targets_router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Cancelled",
        reply_markup=ReplyKeyboardRemove(),
    )


@targets_router.message(Target.repo)
async def process_repo(message: Message, state: FSMContext) -> None:
    pattern = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?/[a-zA-Z0-9_.-]{1,100}$"
    if message.text is None:
        await message.answer(
            "Response with target repo in format: {user}/{repo}, not an empty message"
        )
        return
    repo: str = message.text
    if not re.match(pattern, repo):
        await message.answer(
            f"This message: `{repo}`\n"
            "doesn't match format:"
            "{user}/{repo}, not an empty message"
        )
        return
    try:
        await check_repo_accessable(repo)
    except HTTPStatusError:
        await message.answer(f"Can't get info about {repo=} check if it's available")
        return
    await state.update_data(repo=repo)
    await state.set_state(Target.committer)
    await message.answer("And committer handle?")


@targets_router.message(Target.committer)
async def process_committer(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("response with target committer, noot an empty message")
        return
    data = await state.update_data(committer=message.text)
    if message.from_user is None or message.from_user.username is None:
        error_line = "can't set up target without user: message without user"
        await message.answer(error_line)
        raise ValueError(error_line)
    handle = message.from_user.username
    response_message = "Pair added!"
    try:
        await create_target(
            user_handle=handle, repo=data["repo"], committer=data["committer"]
        )
    except IntegrityError:
        response_message = "Looks like this pair have been added already"
    await state.clear()
    await message.answer(response_message)


@targets_router.message(Command("list"))
async def process_list_targets(message: Message):
    async with async_session() as db:
        if message.from_user is None or message.from_user.username is None:
            error_line = "Can't set up target without user: message without user"
            await message.answer(error_line)
            raise ValueError(error_line)
        handle = message.from_user.username
        targets = await get_user_targets(user_handle=handle, db=db)
        logger.debug(f"{type(targets)=} {targets=}")

        await message.answer(
            "\n".join(map(str, targets))
            if targets
            else "There are no targets set yet, use `/add`"
        )


class RemoveCallback(CallbackData, prefix="rmcal"):
    repo: str
    committer: str


@targets_router.message(Command("remove"))
async def process_remove_target(message: Message):
    buttons = []
    for target in await get_user_targets(user_handle=get_user_handle(message)):
        buttons.append(
            InlineKeyboardButton(
                text=f"<{target.repo} | {target.committer}>",
                callback_data=RemoveCallback(
                    repo=target.repo, committer=target.committer
                ).pack(),
            )
        )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])
    await message.answer("Select a target to be removed:", reply_markup=keyboard)


@targets_router.callback_query(RemoveCallback.filter())
async def remove_target(callback_query: CallbackQuery, callback_data: RemoveCallback):
    await remove_target_from_db(
        callback_data.repo,
        callback_data.committer,
        user_handle=callback_query.from_user.username,
    )
    logger.debug(f"{callback_data=} {callback_query=}")
    await callback_query.answer(
        f"Target <{callback_data.repo} | {callback_data.committer}> has been removed"
    )
