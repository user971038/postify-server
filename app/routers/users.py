from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session

from app.models.user import User
from app.schemas.user import UserCreate, UserRead

from app.models.post import Post
from app.schemas.post import PostRead

from app.models.image import Image
from app.schemas.image import ImageRead

from app.models.like import Like
from app.models.comment import Comment

import uuid

router = APIRouter(prefix="/users", tags=["users"])


# get_users
@router.get('/', response_model=List[UserRead])
async def get_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    return result.scalars().all()

# create_user
@router.post('/', response_model=UserCreate, status_code=201)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(**data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# get_posts_by_user
#@router.get('/{userId}/posts', response_model=List[PostRead], status_code=200)
#async def get_posts_by_user(userId: uuid.UUID, session: AsyncSession = Depends(get_session)):
    #res = await session.execute(select(Post).where(Post.user_id == userId))
    #return res.scalars().all()

# get_posts_by_user
@router.get('/{userId}/posts', response_model=List[PostRead], status_code=200)
async def get_posts_by_user(userId: uuid.UUID, session: AsyncSession = Depends(get_session)):
    # 1. Fetch the raw posts belonging to this user
    result = await session.execute(select(Post).where(Post.user_id == userId))
    posts = result.scalars().all()
    
    post_with_data = []
    
    # 2. Hydrate the data loops so PostRead doesn't get empty structural requirements
    for post in posts:
        image_result = await session.execute(select(Image).where(Image.post_id == post.id))
        images = image_result.scalars().all()
        
        like_result = await session.execute(select(Like).where(Like.post_id == post.id))
        likes = like_result.scalars().all()
        
        comments_result = await session.execute(select(Comment).where(Comment.post_id == post.id))
        comments = comments_result.scalars().all()      
        
        post_with_data.append(
            PostRead(
                id=post.id,
                user_id=post.user_id,
                description=post.description,
                created_at=post.created_at,
                images=[ImageRead(**img.model_dump()) for img in images],
                likes_count=len(likes),
                comments_count=len(comments)
            )
        )
        
    return post_with_data

# get_user_by_id
@router.get('/{user_id}', response_model=UserRead)
async def get_user_by_id(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# - - - - - - - - - - - - - - - - - - - - - -

# get_user_by_username
@router.get('/by-username/{username}', response_model=UserRead)
async def get_user_by_username(username: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user