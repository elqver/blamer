from typing import TYPE_CHECKING
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, select
from .base import Base, db_added


from loguru import logger

if TYPE_CHECKING:
    from .target import Target


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    handle: Mapped[str] = mapped_column(String(30))

    targets: Mapped[list["Target"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return self.handle


@db_added
async def create_user(handle: str, *, db: AsyncSession) -> None:
    db.add(User(handle=handle))


@db_added
async def get_user(handle: str, *, db: AsyncSession) -> int:
    stmt = select(User).where(User.handle == handle)
    return (await db.execute(stmt)).one().id


@db_added
async def get_or_create_user(handle: str, *, db: AsyncSession) -> int:
    instance: User | None = (
        (await db.execute(select(User).where(User.handle == handle))).scalars().first()
    )
    if instance is None:
        instance = User(handle=handle)
        db.add(instance)
        await db.flush()
    return instance.id
