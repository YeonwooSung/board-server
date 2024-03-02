from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# custom imports
from app.database import get_db
from app.utils.logging import Logger
from app.schemas.posts import PostsSchema
from app.models.posts import Posts


router = APIRouter(prefix="/v1/posts")
logger = Logger()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostsSchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    req_id = request.state.request_id
    _post: Posts = Posts(**payload.model_dump())
    await _post.save(db_session)
    logger.log_debug(f"{req_id} | Post {_post.title} created successfully")
    return {"message": "Post created successfully"}
