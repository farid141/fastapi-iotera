from sqlmodel import SQLModel, Field
from typing import Optional

class ItemBase(SQLModel):
    name: str = Field(max_length=50)
    description: str|None = Field(default=None, max_length=50)

class Item(ItemBase, table=True):  # Table model
    __tablename__ = "items"  # Explicitly set the table name
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id")

class ItemCreate(ItemBase):  # Schema for creating an item
    owner_id: int

class ItemRead(ItemBase):  # Schema for reading an item
    id: int
    owner_id: int