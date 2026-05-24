from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session

from app.models.user import User
from app.schemas.user import UserCreate, UserRead

from app.models.post import Post
from app.schemas.post import PostRead

import uuid

router = APIRouter(prefix="/users", tags=["users"])

@router.get('/', response_model=List[UserRead])
async def get_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    return result.scalars().all()

@router.post('/', response_model=UserCreate, status_code=201)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(**data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.get('/{userId}/posts', response_model=List[PostRead], status_code=200)
async def get_posts_by_user(userId: uuid.UUID, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Post).where(Post.user_id == userId))
    return res.scalars().all()