from sqlmodel import SQLModel, Field
from typing import Optional
class UserBase(SQLModel):
    name: str = Field(max_length=50)
    email: str = Field(max_length=50)

class User(UserBase, table=True):  # Table model
    __tablename__ = "users"  # Explicitly set the table name
    id: Optional[int] = Field(default=None, primary_key=True)

class UserCreate(UserBase):  # Schema for creating a user
    pass

class UserRead(UserBase):  # Schema for reading a user
    id: int
