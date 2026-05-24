from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session

from app.models.comment import Comment
from app.models.like import Like
from app.models.post import Post

from app.schemas.comment import CommentCreate, CommentRead
from app.schemas.like import LikeCreate, LikeRead
from app.schemas.post import PostRead, PostReadDetails

#from app.schemas.post import PostCreate, PostRead, PostReadDetails

from app.services.cloudinary_service import cloudinary_service

#PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get('/', response_model=List[PostRead])
async def get_posts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Post))
    return result.scalars().all()

@router.post('/', response_model=PostRead, status_code=201)
async def create_post(
    user_id: str = Form(...),
    description: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(get_session)
    ):
    
    post = Post(description=description, user_id=user_id)
    session.add(post)
    await session.commit()
    await session.refresh(post)

    images = []
    if files and files[0].filename:
        for file in files:
            cloud_res = cloudinary_service.upload_image(
                file,
                folder=["postify/posts/(post.id)"]
            )
            image = Image(
                url=cloud_res["url"],
                public_id=cloud_res["public_id"],
                post_id=post.id
            )

            session.add(image)
            images.append(image)
    await session.commit()

    return PostRead(
        id=post.id,
        user_id=post.user_id,
        description=post.description,
        created_at=post.created_at,
        likes_count=0,
        comments_count=0
    )

# Update and Delete

# @router. y pues ajá

# NEW ---------------------------------------------------------------------------------

@router.get('/{post_id}', response_model=PostReadDetails)
async def get_post_by_id(post_id: uuid.UUID,  session: AsyncSession = Depends(get_session)): 
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    like_result = await session.execute(select(Like).where(Like.post_id == post_id))
    likes = like_result.scalars().all()
    
    comments_result = await session.execute(select(Comment).where(Comment.post_id == post_id))
    comments = comments_result.scalars().all()
    
    return PostReadDetails(
        id=post_id,
        user_id=post.user_id,
        description=post.description,
        created_at=post.created_at,
        likes=[LikeRead(**like.model_dump()) for like in likes],
        comments=[CommentRead(**comment.model_dump()) for comment in comments]
    )


@router.post('/{post_id}/likes', response_model=LikeRead, status_code=201)
async def add_like(post_id: uuid.UUID, data: LikeCreate,  session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_like = await session.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == data.user_id)
    )
    
    if existing_like.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Like already exists")
    
    like = Like(user_id=data.user_id, post_id=post_id)
    session.add(like)
    await session.commit()
    await session.refresh(like)
    
    return LikeRead(**like.model_dump())
        
        
@router.post('/{post_id}/comments', response_model=CommentRead, status_code=201)
async def add_comment(post_id: uuid.UUID, data:CommentCreate,  session: AsyncSession = Depends(get_session)): 
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(**data.model_dump())
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    
    return CommentRead(**comment.model_dump())