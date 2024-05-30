from typing import get_origin
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, ForeignKey, UniqueConstraint, delete, select
from .base import Base, db_added
from .user import User, get_or_create_user


class Target(Base):
    __tablename__ = "target"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "repo", "committer", name="unique_user_repo_committer"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    repo: Mapped[str] = mapped_column(String(255))
    committer: Mapped[str] = mapped_column(String(255))
    user: Mapped[User] = relationship(back_populates="targets")

    def __repr__(self) -> str:
        return f"repo={self.repo!r} committer={self.committer!r}"


@db_added
async def create_target(
    repo: str,
    committer: str,
    user_id: int | None = None,  # type: ignore
    user_handle: str | None = None,
    *,
    db: AsyncSession | None = None,
) -> None:
    if db is None:
        raise ValueError("No db access provieded")
    if user_id is None and user_handle is None:
        raise ValueError(
            f"Can't create target for unknown user: {user_id=}, {user_handle=}"
        )
    if user_id is None and user_handle is not None:
        user_id: int = await get_or_create_user(handle=user_handle, db=db)
    db.add(Target(user_id=user_id, repo=repo, committer=committer))


@db_added
async def get_user_targets(user_handle: str, *, db: AsyncSession | None = None):
    if db is None:
        raise ValueError("No db access provieded")
    user_id: int = await get_or_create_user(user_handle, db=db)
    stmt = (
        select(Target).join(User, Target.user_id == User.id).where(User.id == user_id)
    )
    return (await db.execute(stmt)).scalars().all()


@db_added
async def remove_target(
    repo: str,
    committer: str,
    user_id: int | None = None,  # type: ignore
    user_handle: str | None = None,
    *,
    db: AsyncSession | None = None,
):
    if db is None:
        raise ValueError("No db access provieded")
    if user_id is None and user_handle is None:
        raise ValueError(
            f"Can't create target for unknown user: {user_id=}, {user_handle=}"
        )
    if user_id is None and user_handle is not None:
        user_id: int = await get_or_create_user(handle=user_handle, db=db)
    return await db.execute(
        delete(Target).where(
            (Target.repo == repo)
            & (Target.committer == committer)
            & (Target.user_id == user_id)
        )
    )
