from sqlmodel import SQLModel, Field, Sequence, select, Session
from sqlalchemy import event

class UserBase(SQLModel):
    name: str = Field(max_length=50)
    email: str = Field(max_length=50)

class User(UserBase, table=True):  # Table model
    __tablename__ = "users"  # Explicitly set the table name
    seq_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"server_default": Sequence("users_id_seq").next_value()})
    id: str|None = Field(max_length=50, unique=True, default=None)

class UserCreate(UserBase):  # Schema for creating a user
    pass

class UserRead(UserBase):  # Schema for reading a user
    id: str = Field(max_length=50)

class UserUpdate(UserBase):
    name: str|None = Field(max_length=50, default=None)
    email: str|None = Field(max_length=50, default=None)

def generate_user_id(mapper, connection, target):
    if target.seq_id is None:
        session = Session(connection)
        result = session.execute(select(User).order_by(User.seq_id.desc()).limit(1)).first()
        last_seq_id = result[0].seq_id if result else 0
        target.seq_id = last_seq_id + 1
    
    target.id = f"USR_{target.seq_id:04d}"

event.listen(User, "before_insert", generate_user_id)