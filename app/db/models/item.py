from sqlmodel import SQLModel, Field

class ItemBase(SQLModel):
    name: str = Field(max_length=50)
    description: str|None = Field(default=None, max_length=50)

class Item(ItemBase, table=True):
    __tablename__ = "items"
    id: str|None = Field(max_length=50, default=None, primary_key=True)

    owner_id: str = Field(foreign_key="users.id", max_length=50)

class ItemCreate(ItemBase):
    owner_id: str = Field(max_length=50) 

class ItemRead(ItemBase):
    id: str
    owner_id: str = Field(max_length=50)

class ItemUpdate(ItemBase):
    name: str|None = Field(max_length=50, default=None)
    description: str|None = Field(max_length=50, default=None)
    owner_id: str|None = Field(default=None, max_length=50)