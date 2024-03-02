from sqlalchemy import String, select, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column

# custom imports
from app.models.base import Base


class Posts(Base):
    __tablename__ = "posts"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    title = mapped_column(String, nullable=False)
    content = mapped_column(String, nullable=False)
    author_id = mapped_column(Integer, nullable=False)
    category_id = mapped_column(Integer, nullable=False)

    @classmethod
    async def find_by_title(cls, db_session: AsyncSession, title: str):
        stmt = select(cls).where(cls.title == title)
        result = await db_session.execute(stmt)
        return result.scalar_one_or_none()
