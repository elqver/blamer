import asyncio
from datetime import datetime, timedelta, timezone

from github_api import get_repository_branches, get_target_stats
from pprint import pprint


async def main():
    since = datetime.now(timezone.utc) - timedelta(days=1)
    stats = await get_target_stats("elqver/blamer", "elqver", since)
    pprint(stats)


if __name__ == "__main__":
    asyncio.run(main())
