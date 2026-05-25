from typing import List, Optional, Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session

from app.models.comment import Comment
from app.models.image import Image
from app.models.like import Like
from app.models.post import Post

from app.schemas.comment import CommentCreate, CommentRead
from app.schemas.image import ImageRead
from app.schemas.like import LikeCreate, LikeRead
from app.schemas.post import PostCreate, PostRead, PostReadDetails, PostUpdate, PostDelete

from app.services.cloudinary_service import cloudinary_service

router = APIRouter(prefix="/posts", tags=["posts"])

# PostRead - get_posts

@router.get('/', response_model=List[PostRead])
async def get_posts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Post))
    posts =  result.scalars().all()
    
    post_with_data = []
    
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
                images=[ImageRead(**img.model_dump()) for img in images ],
                #likes=[LikeRead(**like.model_dump()) for like in likes],
                #comments=[CommentRead(**comment.model_dump()) for comment in comments]
                #checar cómo está todo declarado en schemas/post.py
                likes_count=len(likes),
                comments_count=len(comments)
            )
        )
    return post_with_data

# PostRead - create_post

@router.post('/', response_model=PostRead, status_code=201)
async def create_post(
    #user_id: str = Form(...),
    user_id: uuid.UUID = Form(...),
    description: str = Form(...),
    #files: Optional[List[UploadFile]] = File(default=None),
    files: Optional[List[Any]] = File(default=None),
    session: AsyncSession = Depends(get_session)
    ):
    
    post = Post(description=description, user_id=user_id)
    session.add(post)
    await session.commit()
    await session.refresh(post)

    images = []

    #if files and files[0].filename:
        #for file in files:
            #cloud_res = cloudinary_service.upload_image(
                #file,
                #folder=f'postify/posts/{post.id}'
            #)

    if files: 
        for file in files:

            if isinstance(file, str) or not hasattr(file, "filename") or not file.filename:
                continue
                
            cloud_res = await cloudinary_service.upload_image(
                file,
                folder=f'postify/posts/{post.id}'
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
        images=[ImageRead(**img.model_dump()) for img in images],
        created_at=post.created_at,
        likes_count=0,
        comments_count=0
    )

# Update and Delete

# PostRead - update_post

@router.patch('/{post_id}', response_model=PostRead)
async def update_post(
    post_id: uuid.UUID, 
    data: PostUpdate, 
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(post, key, value)
        
    session.add(post)
    await session.commit()
    await session.refresh(post)
    
    image_result = await session.execute(select(Image).where(Image.post_id == post_id))
    images = image_result.scalars().all()
    
    like_count_res = await session.execute(select(Like).where(Like.post_id == post_id))
    comment_count_res = await session.execute(select(Comment).where(Comment.post_id == post_id))
    
    return PostRead(
        id=post.id,
        user_id=post.user_id,
        description=post.description,
        created_at=post.created_at,
        images=[ImageRead(**img.model_dump()) for img in images],
        likes_count=len(like_count_res.scalars().all()),
        comments_count=len(comment_count_res.scalars().all())
    )

# PostDelete - delete_post

@router.delete('/{post_id}', response_model=PostDelete)
async def delete_post(post_id: uuid.UUID, session: AsyncSession = Depends(get_session)):

    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
            
    await session.delete(post)
    await session.commit()
    
    return PostDelete(id=post_id)

# NEW ---------------------------------------------------------------------------------

# PostReadDetails - get_post_by_id

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

    image_result = await session.execute(select(Image).where(Image.post_id == post_id))
    images = image_result.scalars().all()
    
    return PostReadDetails(
        id=post_id,
        user_id=post.user_id,
        description=post.description,
        created_at=post.created_at,
        images=[ImageRead(**img.model_dump()) for img in images],
        likes=[LikeRead(**like.model_dump()) for like in likes],
        comments=[CommentRead(**comment.model_dump()) for comment in comments]
    )

# LikeRead - add_like

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
        
# CommentRead add_comment

@router.post('/{post_id}/comments', response_model=CommentRead, status_code=201)
async def add_comment(post_id: uuid.UUID, data:CommentCreate,  session: AsyncSession = Depends(get_session)): 
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    #comment = Comment(**data.model_dump(), post_id=post_id)
    comment_data = data.model_dump()
    comment_data["post_id"] = post_id
    
    comment = Comment(**comment_data)
    
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    
    return CommentRead(**comment.model_dump())