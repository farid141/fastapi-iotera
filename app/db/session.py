from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/iotera-fastapi"
engine = create_engine(DATABASE_URL, echo=True)

def get_db():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)  # Create all tables
