from functools import wraps

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import DB_URL


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def async_get_session():
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


def db_added(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "db" not in kwargs or kwargs["db"] is None:
            async with async_session() as db:
                kwargs["db"] = db
                res = await func(*args, **kwargs)
                await db.commit()
            return res
        return await func(*args, **kwargs)

    return wrapper
