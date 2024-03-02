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


@router.get("/{post_id}", status_code=status.HTTP_200_OK)
async def get_post(post_id: int, request: Request, db_session: AsyncSession = Depends(get_db)):
    req_id = request.state.request_id
    _post: Posts = await Posts.find(db_session, [Posts.id == post_id])
    if not _post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    logger.log_debug(f"{req_id} | Post {_post.title} retrieved successfully")
    return _post


@router.patch("/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, payload: PostsSchema, request: Request, db_session: AsyncSession = Depends(get_db)):
    req_id = request.state.request_id
    _post: Posts = await Posts.find(db_session, [Posts.id == post_id])
    if not _post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await _post.update(db_session, payload.model_dump())
    logger.log_debug(f"{req_id} | Post {_post.title} updated successfully")
    return {"message": "Post updated successfully"}


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, request: Request, db_session: AsyncSession = Depends(get_db)):
    req_id = request.state.request_id
    _post: Posts = await Posts.find(db_session, [Posts.id == post_id])
    if not _post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await _post.delete(db_session)
    logger.log_debug(f"{req_id} | Post {_post.title} deleted successfully")
    return {"message": "Post deleted successfully"}
