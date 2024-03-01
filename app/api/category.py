from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# custom imports
from app.database import get_db
from app.utils.logging import Logger
from app.schemas.category import (
    CategorySchema,
    CategoryResponse,
)
from app.models.category import Category
from app.services.category import update_category_data


router = APIRouter(prefix="/v1/category")
logger = Logger()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
async def create_category(payload: CategorySchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    req_id = request.state.request_id
    jwt_payload = request.state.jwt_payload
    _id = jwt_payload.get("id")
    if not _id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user")

    logger.info(f"Request ID: {req_id} | JWT Payload: {jwt_payload} | Creating category: {payload.name}")
    # create category
    _category: Category = Category(**payload.model_dump(), author_id=_id)

    # save category
    await _category.save(db_session)
    logger.log_debug(f"Request ID: {req_id} | JWT Payload: {jwt_payload} | Category created: {payload.name}")
    return _category


@router.patch("/{category_id}", status_code=status.HTTP_200_OK, response_model=CategoryResponse)
async def update_category(category_id: int, payload: CategorySchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    req_id = request.state.request_id
    jwt_payload = request.state.jwt_payload
    _id = jwt_payload.get("id")
    if not _id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized user")

    # find and update the category data
    _category = await update_category_data(db_session, category_id, payload, _id)
    logger.log_debug(f"Request ID: {req_id} | JWT Payload: {jwt_payload} | Category updated: {category_id}")
    return _category
