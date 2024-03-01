from sqlalchemy import String, select, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column

# custom imports
from app.models.base import Base


class Category(Base):
    __tablename__ = "category"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String, nullable=False)
    author_id = mapped_column(Integer, nullable=False)

    @classmethod
    async def find_by_name(cls, db_session: AsyncSession, name: str):
        stmt = select(cls).where(cls.name == name)
        result = await db_session.execute(stmt)
        return result.scalar_one_or_none()
