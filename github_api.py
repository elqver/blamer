import datetime
import os
import urllib
from loguru import logger

from dotenv import load_dotenv
import requests

if os.path.exists('github_creds.env'):
    load_dotenv('github_creds.env')


GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def request_github(endpoint, params=None, extra_headers=None):
    url = f'https://api.github.com{'' if endpoint.startswith('/') else '/'}{endpoint}'
    if params:
        url += '?' + urllib.parse.urlencode(params)
    logger.debug(f'Fetching {url}')
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    if extra_headers:
        logger.debug(f'Adding extra headers: {extra_headers}')
        headers.update(extra_headers)
    response = requests.get(url, headers=headers)
    return response.json()


def get_user_info(username):
    return request_github(f'users/{username}')


def get_user_repos(username, since=None, until=None):
    params = {"since": since} if since else {} | {"until": until} if until else {}
    return request_github(f'users/{username}/repos', params=params)


def get_commits(username, repo_name):
    return request_github(f'repos/{username}/{repo_name}/commits')


def get_repos_commits(username, repo_name, since=None, until=None):
    params = {"since": since} if since else {} | {"until": until} if until else {}
    return request_github(f'repos/{username}/{repo_name}/commits', params)


def get_commit_lines_delta(username, repo_name, commit_sha):
    return sum(
        file['additions'] - file['deletions']
        for file
        in request_github(f'repos/{username}/{repo_name}/commits/{commit_sha}')['files']
    )


def get_repository_lines_delta(username, repo_name, since=None, until=None):
    return max(sum(
        get_commit_lines_delta(username, repo_name, commit['sha'])
        for commit
        in get_repos_commits(username, repo_name, since, until)
    ), 0)


def get_user_total_lines_delta(username, since=None, until=None):
    return sum(
        get_repository_lines_delta(username, repo['name'], since, until)
        for repo
        in get_user_repos(username)
    )


def main():
    target_user = 'elqver'
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S')
    logger.info(f'User {target_user} has added '
                f'{get_user_total_lines_delta(target_user, since=today)} '
                f'lines of code today')


if __name__ == '__main__':
    main()
