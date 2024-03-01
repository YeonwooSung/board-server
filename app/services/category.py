from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# custom imports
from app.utils.logging import Logger
from app.schemas.category import CategorySchema
from app.models.category import Category


logger = Logger()


async def update_category_data(db_session: AsyncSession, category_id: int, payload: CategorySchema, user_id: int) -> Category:
    # find category
    _category: Category = Category.find(db_session, [Category.id == category_id])
    if not _category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if _category.author_id != user_id:
        # only the author can update the category
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user")

    # update category
    _category.name = payload.name

    # save category
    _category.update(db_session)

    return _category
