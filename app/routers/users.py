from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, Sequence
from typing import Annotated

from app.db.session import get_db, engine
from app.db.utils import create_sequence, drop_sequence, inspect_table
from app.db.models.user import UserCreate, UserRead, UserUpdate, User
from app.db.models.item import Item

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User.model_validate(user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}")
def read_user(user_id: str, db: Session = Depends(get_db)):
    statement = select(User).where(User.id == user_id)
    result = db.exec(statement).all()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result

@router.get("/", response_model=list[UserRead])
def get_user(
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    ):
    statement = select(User).offset(offset).limit(limit)
    results = db.exec(statement).all()

    if not results:
        raise HTTPException(status_code=404, detail="User not found")
    
    return results

@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: str, user: UserUpdate, db:Session=Depends(get_db)):
    user_db = db.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user.model_dump(exclude_unset=True) # mengekstrak field kosong dan default value dari request body
    user_db.sqlmodel_update(user_data)  # validasi field ke table model
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

@router.post("/create_table")
def create_user_table(db:Session=Depends(get_db)):
    try:
        if inspect_table(User.__tablename__):
            raise Exception("Table already exists!")

        create_sequence(db, "users_id_seq")
        User.metadata.create_all(engine, [User.__table__], False)
        
        return {"message": "User table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create table fails!\n{str(e)}")

@router.delete("/drop_table")
def drop_user_table(db:Session=Depends(get_db)):
    try:
        if not inspect_table(User.__tablename__):
            raise Exception("Table doesn't exists!")

        drop_sequence(db, "users_id_seq")
        User.metadata.drop_all(engine, [User.__table__], False)
        
        return {"message": "User table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drop table fails!\n{str(e)}")