from typing import Any

from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declared_attr, DeclarativeBase

from time import time

# custom imports
from app.utils.logging import Logger

logger = Logger()


class Base(DeclarativeBase):
    id: Any
    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    async def save(self, db_session: AsyncSession, close_session: bool = True):
        """

        :param db_session:
        :param close_session:
        :return:
        """
        start_time = time()
        try:
            db_session.add(self)
            logger.log_debug(f"Creating {self.__class__.__name__} | Time: {time() - start_time} seconds | Data: {self.__dict__}")
            return await db_session.commit()
        except SQLAlchemyError as ex:
            logger.log_error(f"Error creating {self.__class__.__name__} | Time: {time() - start_time} seconds | Data: {self.__dict__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)) from ex
        finally:
            if close_session:
                await db_session.close()

    async def delete(self, db_session: AsyncSession, close_session: bool = True):
        """

        :param db_session:
        :param close_session:
        :return:
        """
        start_time = time()
        try:
            await db_session.delete(self)
            await db_session.commit()
            logger.log_debug(f"Deleted {self.__class__.__name__} | Time: {time() - start_time} seconds | Data: {self.__dict__}")
            return True
        except SQLAlchemyError as ex:
            logger.log_error(f"Error deleting {self.__class__.__name__} | Time: {time() - start_time} seconds | Data: {self.__dict__}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)) from ex
        finally:
            if close_session:
                await db_session.close()

    async def update(self, db: AsyncSession, close_session: bool=True, **kwargs):
        """

        :param db:
        :param kwargs
        :return:
        """
        try:
            for k, v in kwargs.items():
                setattr(self, k, v)
            return await db.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)) from ex
        finally:
            if close_session:
                await db.close()

    async def save_or_update(self, db: AsyncSession, close_session: bool=True):
        try:
            db.add(self)
            return await db.commit()
        except IntegrityError as exception:
            if isinstance(exception.orig, UniqueViolationError):
                return await db.merge(self)
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=repr(exception),
                ) from exception
        finally:
            if close_session:
                await db.close()
