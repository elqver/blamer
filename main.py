import os
from pprint import pprint
import urllib

from dotenv import load_dotenv
import requests

if os.path.exists('github_creds.env'):
    load_dotenv('github_creds.env')


GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


def request_github(endpoint):
    url = f'https://api.github.com{'' if endpoint.startswith('/') else '/'}{endpoint}'
    print(f'Fetching {url}')
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()


def get_user_info(username):
    return request_github(f'users/{username}')


def get_commits(username, repo_name):
    return request_github(f'repos/{username}/{repo_name}/commits')


def get_user_repos(username):
    return request_github(f'users/{username}/repos')


def get_repos_commits(username, repo_name):
    return request_github(f'repos/{username}/{repo_name}/commits')


def main():
    target_user = 'elqver'
    target_repo = 'blamer'

    total_additions = 0
    total_deletions = 0
    for commit in get_repos_commits(target_user, target_repo):
        actual_commit_path = urllib.parse.urlparse(commit['url']).path
        for file in request_github(actual_commit_path)['files']:
            total_additions += file['additions']
            total_deletions += file['deletions']
    print(
        f'Total additions: {total_additions}\n'
        f'Total deletions: {total_deletions}'
    )


if __name__ == '__main__':
    main()
