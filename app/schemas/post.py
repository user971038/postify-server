from datetime import datetime  
import uuid
from typing import Optional

from sqlmodel import SQLModel

from app.schemas.like import LikeRead
from app.schemas.comment import CommentRead
from app.schemas.image import ImageRead

class PostCreate(SQLModel):
    description: str
    user_id: uuid.UUID
    
class PostRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    description: str
    created_at: datetime
    images: list["ImageRead"] = []
    likes_count: int = 0
    comments_count: int = 0

# Update and Delete

class PostUpdate(SQLModel):
    description: Optional[str] = None

class PostDeleteResponse(SQLModel):
    id: uuid.UUID

# Details

class PostReadDetails(PostRead):
    id: uuid
    user_id: uuid.UUID
    description: str
    created_at: datetime
    images: list["ImageRead"] = []
    likes: list["LikeRead"] = []
    comments: list["CommentRead"] = []