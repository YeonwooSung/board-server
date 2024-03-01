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
