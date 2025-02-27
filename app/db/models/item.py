from sqlmodel import SQLModel, Field, Sequence, select, Session
from sqlalchemy import event

class ItemBase(SQLModel):
    name: str = Field(max_length=50)
    description: str|None = Field(default=None, max_length=50)

class Item(ItemBase, table=True):  # Table model
    __tablename__ = "items"  # Explicitly set the table name
    seq_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": Sequence("items_id_seq").next_value()})
    id: str|None = Field(max_length=50, unique=True, default=None)

    owner_id: str = Field(foreign_key="users.id", max_length=50)

class ItemCreate(ItemBase):  # Schema for creating an item
    owner_id: str = Field(max_length=50) 

class ItemRead(ItemBase):  # Schema for reading an item
    id: int
    owner_id: str = Field(max_length=50)

class ItemUpdate(ItemBase):
    name: str|None = Field(max_length=50, default=None)
    description: str|None = Field(max_length=50, default=None)
    owner_id: str|None = Field(default=None, max_length=50)

def generate_item_id(mapper, connection, target):
    if target.seq_id is None:
        session = Session(connection)
        result = session.execute(select(Item).order_by(Item.seq_id.desc()).limit(1)).first()
        last_seq_id = result[0].seq_id if result else 0
        target.seq_id = last_seq_id + 1
    
    target.id = f"ITM_{target.seq_id:04d}"

event.listen(Item, "before_insert", generate_item_id)