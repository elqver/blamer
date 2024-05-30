import asyncio
import datetime
import os
from urllib import parse as urllibparse

from dotenv import load_dotenv
import httpx
from loguru import logger

if os.path.exists("github_creds.env"):
    load_dotenv("github_creds.env")


GITHUB_TOKEN = os.getenv("GH_TOKEN")
GITHUB_URL = "https://api.github.com"


async def request_github(endpoint: str, params=None, extra_headers=None):
    url = f"{GITHUB_URL}{'' if endpoint.startswith('/') else '/'}{endpoint}"

    if params:
        url += "?" + urllibparse.urlencode(params)
    logger.debug(f"Fetching {url}")

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    # headers = {}
    if extra_headers:
        logger.debug(f"Adding extra headers: {extra_headers}")
        headers.update(extra_headers)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def get_target_stats(
    repo: str,
    committer: str,
    since: datetime.datetime,
    until: datetime.datetime | None = None,
):
    res = await request_github(
        endpoint=f"repos/{repo}/commits",
        params={
            "committer": committer,
            "since": since.isoformat() + "Z",
        }
        | ({"until": until.isoformat() + "Z"} if until is not None else {}),
    )

    async def fetch_commit_stats(commit, repo):
        return (await request_github(endpoint=f"repos/{repo}/commits/{commit['sha']}"))[
            "stats"
        ]

    repo_stats = await asyncio.gather(
        *[fetch_commit_stats(commit, repo) for commit in res]
    )
    return repo_stats


async def check_repo_accessable(repo: str):
    await request_github(endpoint=f"repos/{repo}")
