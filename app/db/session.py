from sqlmodel import Session, create_engine, text
from fastapi import Query
import redis

from dotenv import load_dotenv
import os

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    db=os.getenv("REDIS_DB"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def get_session(schema: str):
    """Mengembalikan session database dengan schema tertentu dalam context manager."""
    with engine.connect() as connection:
        connection.execute(text(f'ALTER SESSION SET CURRENT_SCHEMA = {schema}'))
        connection.commit()
        with Session(bind=connection) as session:
            yield session

def get_db(schema: str=Query(description="Schema database", default="C##FARID")):
    """Dependency untuk session database dengan schema tertentu."""
    yield from get_session(schema)