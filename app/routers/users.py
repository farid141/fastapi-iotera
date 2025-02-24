from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, text
from app.db.session import get_db
from app.db.models.user import UserCreate, UserRead, User

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
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
