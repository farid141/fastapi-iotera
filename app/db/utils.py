from sqlmodel import Session, text, inspect
from .session import engine

def create_sequence(db: Session, sequence_name: str):
    """Creates a sequence in the database if it does not exist."""
    try:
        db.exec(text(f"CREATE SEQUENCE {sequence_name} START WITH 1 INCREMENT BY 1"))
    except Exception:
        pass

def inspect_table(table_name:str):
    """Check if table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def drop_sequence(db:Session, sequence_name:str):
    """Drops a sequence in the database if it exist."""
    try:
        db.exec(text(f"DROP SEQUENCE {sequence_name}"))
    except Exception:
        pass
