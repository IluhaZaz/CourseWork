from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class ItemCreate(BaseModel):
    name: str
    comment: Optional[str] = None
    priority: int = Field(le=3, ge=1, default=1)
    do_till: Optional[datetime] = None


class ItemRead(ItemCreate):
    id: UUID
    is_done: bool

    class Config:
        orm_mode = True


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    comment: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=3)
    do_till: Optional[datetime] = None
