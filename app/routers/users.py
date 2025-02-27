from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_db, engine
from app.db.models.user import UserCreate, UserRead, User
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
def read_user(user_id: int, db: Session = Depends(get_db)):
    statement = select(User, Item).where(User.id == user_id).join(Item)
    results = db.exec(statement).all()

    if not results:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = results[0][0]  # Ambil user dari tuple pertama
    items = [item for _, item in results]  # Kumpulkan semua item
    
    return {
        "id": user.id,
        "name": user.name,
        "items": [{"id": item.id, "name": item.name, "description":item.description} for item in items]
    }

@router.post("/create_table")
def create_user_table(db: Session = Depends(get_db)):
    try:
        User.metadata.create_all(engine, [User.__table__], False)
        
        return {"message": "User table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="User table already exists!")

@router.post("/drop_table")
def drop_user_table(db: Session = Depends(get_db)):
    try:
        User.metadata.drop_all(engine, [User.__table__], False)
        
        return {"message": "User table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="User table doesn't exists")