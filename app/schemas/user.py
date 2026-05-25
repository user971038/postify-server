from datetime import datetime
import uuid
from sqlmodel import SQLModel
from typing import Optional

class UserCreate(SQLModel):
    username: str
    name: str
    lastname: str
    email: str
    password: str

class UserRead(SQLModel):
    id: uuid.UUID
    username: str
    name: str
    lastname: str
    email: str
    created_at: datetime

class UserUpdate(SQLModel):
    username: Optional[str] = None
    name: Optional[str] = None
    lastname: Optional[str] = None