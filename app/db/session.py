from sqlmodel import Session, create_engine
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

def get_db():
    with Session(engine) as session:
        yield session
