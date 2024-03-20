import asyncio
import datetime
import os
import urllib
import httpx
from loguru import logger

from dotenv import load_dotenv
import requests

if os.path.exists('github_creds.env'):
    load_dotenv('github_creds.env')


GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

max_parallel_requests = 0
current_parallel_requests = 0


async def request_github(endpoint, params=None, extra_headers=None):

    url = f'https://api.github.com{'' if endpoint.startswith('/') else '/'}{endpoint}'

    if params:
        url += '?' + urllib.parse.urlencode(params)
    logger.debug(f'Fetching {url}')

    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    if extra_headers:
        logger.debug(f'Adding extra headers: {extra_headers}')
        headers.update(extra_headers)

    async with httpx.AsyncClient() as client:
        global current_parallel_requests
        global max_parallel_requests
        current_parallel_requests += 1
        if current_parallel_requests >= max_parallel_requests:
            max_parallel_requests = current_parallel_requests

        response = await client.get(url, headers=headers)
        response.raise_for_status()

        current_parallel_requests -= 1

        return response.json()


async def get_user_repos(username, since=None, until=None):
    params = {"since": since} if since else {} | {"until": until} if until else {}
    return await request_github(f'users/{username}/repos', params=params)


async def get_repos_commits(username, repo_name, since=None, until=None):
    params = {"since": since} if since else {} | {"until": until} if until else {}
    return await request_github(f'repos/{username}/{repo_name}/commits', params)


async def get_commit_lines_delta(username, repo_name, commit_sha):
    return max(sum(
        file['additions'] - file['deletions']
        for file
        in (await request_github(f'repos/{username}/{repo_name}/commits/{commit_sha}'))['files']
    ), 0)


async def get_repository_lines_delta(username, repo_name, since=None, until=None):
    commit_calculations = asyncio.gather(
        *[
            get_commit_lines_delta(username, repo_name, commit['sha'])
            for commit
            in await get_repos_commits(username, repo_name, since, until)
        ]
    )
    return sum(await commit_calculations)


async def get_user_total_lines_delta(username, since=None, until=None):
    user_repos = await get_user_repos(username)
    logger.debug(f'User {username} has {len(user_repos)} repos')
    repositories_line_deltas = await asyncio.gather(*[
        get_repository_lines_delta(username, repo['name'], since, until)
        for repo
        in user_repos
    ])
    return sum(repositories_line_deltas)


async def main():
    target_user = 'elqver'
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S')
    logger.info(f'User {target_user} has added '
                f'{await get_user_total_lines_delta(target_user, since=today)} '
                f'lines of code today')
    logger.info(f'Max parallel requests: {max_parallel_requests}')


if __name__ == '__main__':
    asyncio.run(main())

