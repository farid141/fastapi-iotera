from sqlmodel import Session, select, inspect, insert, delete, update, SQLModel

from app.db.session import engine
from app.db.session import redis_client
from app.db.models.sequence import Sequence

def inspect_table(table_name:str):
    """Check if table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def create_sequence(db: Session, sequence_name: str):
    try:
        db.exec(insert(Sequence).values(name=sequence_name, value=0))
        db.commit()
    except Exception:
        pass

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

def drop_table(db, engine, model:SQLModel, sequence):
    if not inspect_table(model.__tablename__):
        raise Exception("Table doesn't exists!")
    
    if sequence:
        drop_sequence(db, sequence)
    model.metadata.drop_all(engine, [model.__table__], False)

def create_table(db, engine, model:SQLModel, sequence):
    if not inspect_table(model.__tablename__):
        raise Exception("Table already exists!")
    
    if sequence:
        create_sequence(db, sequence)
    model.metadata.create_all(engine, [model.__table__], False)

def invalidate_pattern_cache(pattern):
    """Deletes all Redis keys that match the pattern."""
    keys_to_delete = redis_client.scan_iter(pattern)  
    for key in keys_to_delete:
        redis_client.delete(key)