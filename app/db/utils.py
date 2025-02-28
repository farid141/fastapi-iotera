from sqlmodel import Session, select, inspect, insert, delete, update

from .session import engine
from .models.sequence import Sequence

def create_sequence(db: Session, sequence_name: str):
    try:
        db.exec(insert(Sequence).values(name=sequence_name, value=0))
        db.commit()
    except Exception:
        pass

def inspect_table(table_name:str):
    """Check if table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def drop_sequence(db:Session, sequence_name:str):
    try:
        db.exec(delete(Sequence).where(Sequence.name == sequence_name))
        db.commit()
    except Exception:
        pass

def next_sequence(db:Session, prefix:str, sequence_name:str)->str:
    stmt = select(Sequence.value).where(Sequence.name == sequence_name)
    result = db.exec(stmt).first()
    
    last_seq_id = result + 1 if result else 1

    # Update the sequence value in the database
    db.exec(
        update(Sequence)
        .where(Sequence.name == sequence_name)
        .values(value=last_seq_id)
    )

    return f"{prefix}_{last_seq_id:04d}"