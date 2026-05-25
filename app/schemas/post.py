from datetime import datetime  
import uuid
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel

if TYPE_CHECKING:
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
    images: List['ImageRead'] = []
    likes_count: int = 0
    comments_count: int = 0

# Update and Delete

class PostUpdate(SQLModel):
    description: Optional[str] = None

class PostDelete(SQLModel):
    id: uuid.UUID
    message: str = "Publicación eliminada exitosamente"

# Details

class PostReadDetails(PostRead): # tmb me da error
    id: uuid.UUID
    user_id: uuid.UUID
    description: str
    created_at: datetime
    images: List['ImageRead'] = []
    likes: List['LikeRead'] = []
    comments: List['CommentRead'] = []
    username: str = "placeholder"

from app.schemas.like import LikeRead
from app.schemas.comment import CommentRead
from app.schemas.image import ImageRead


PostReadDetails.model_rebuild()
PostRead.model_rebuild()