from sqlmodel import SQLModel
import uuid

class ImageCreate(SQLModel):
    id: uuid.UUID
    url: str
    public_id: str
    post_id: uuid.UUID

class ImageRead(SQLModel):
    id: uuid.UUID
    url: str
    public_id: str
    post_id: uuid.UUID