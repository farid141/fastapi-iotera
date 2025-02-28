from sqlmodel import SQLModel, Field

class SequenceBase(SQLModel):
    name: str = Field(max_length=50, primary_key=True)
    value: int

class Sequence(SequenceBase, table=True):
    __tablename__ = "sequences"

class SequenceCreate(SequenceBase):
    pass

class SequenceRead(SequenceBase):
    pass

class SequenceUpdate(SQLModel):
    value: int