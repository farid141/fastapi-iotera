from sqlmodel import SQLModel, Field, Sequence, select, Session
from sqlalchemy import event

class UserBase(SQLModel):
    name: str = Field(max_length=50)
    email: str = Field(max_length=50)

class User(UserBase, table=True):  
    __tablename__ = "users"  
    id: str|None = Field(max_length=50, default=None, primary_key=True)

class UserCreate(UserBase):
    pass

class UserRead(UserBase):  
    id: str = Field(max_length=50)

class UserUpdate(UserBase):
    name: str|None = Field(max_length=50, default=None)
    email: str|None = Field(max_length=50, default=None)