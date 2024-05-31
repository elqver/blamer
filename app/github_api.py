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


async def get_repository_branches(repo: str) -> list[str]:
    return [branch["name"] for branch in await request_github(f"repos/{repo}/branches")]


async def get_commits_sha(
    repo: str,
    committer: str,
    branch_sha: str,
    since: datetime.datetime,
    until: datetime.datetime | None = None,
):
    return {
        commit["sha"]
        for commit in await request_github(
            endpoint=f"repos/{repo}/commits",
            params={
                "committer": committer,
                "since": since.isoformat() + "Z",
                "sha": branch_sha,
            }
            | ({"until": until.isoformat() + "Z"} if until is not None else {}),
        )
    }


async def get_target_stats(
    repo: str,
    committer: str,
    since: datetime.datetime,
    until: datetime.datetime | None = None,
):
    branches = await get_repository_branches(repo)
    commits = set.union(
        *(
            await asyncio.gather(
                *[
                    get_commits_sha(repo, committer, branch, since=since, until=until)
                    for branch in branches
                ]
            )
        )
    )

    async def fetch_commit_stats(commit: str, repo):
        return (await request_github(endpoint=f"repos/{repo}/commits/{commit}"))[
            "stats"
        ]

    repo_stats = await asyncio.gather(
        *[fetch_commit_stats(commit, repo) for commit in commits]
    )
    return repo_stats


async def check_repo_accessable(repo: str):
    await request_github(endpoint=f"repos/{repo}")
