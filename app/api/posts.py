from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# custom imports
from app.database import get_db
from app.utils.logging import Logger


router = APIRouter(prefix="/v1/posts")
logger = Logger()
