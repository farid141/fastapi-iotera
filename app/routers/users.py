from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Annotated

from app.db.session import get_db, engine
from app.db.utils import drop_table, create_table
from app.db.models.user import UserCreate, UserRead, UserUpdate, User

from app.services.user import UserService
from app.db.repositories.user import UserRepository

router = APIRouter()

def get_user_service(session: Session = Depends(get_db))->UserService:
    user_repository = UserRepository(session)
    return UserService(user_repository)

@router.get("/", response_model=list[UserRead])
def get_users(
    user_service:UserService = Depends(get_user_service),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    ):
    results = user_service.get_users(limit, offset)

    if not results:
        raise HTTPException(status_code=404, detail="User not found")
    
    return results

@router.get("/{user_id}")
def read_user(user_id: str, user_service:UserService = Depends(get_user_service)):
    result = user_service.get_user_by_id(user_id)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result

@router.post("/", response_model=UserRead)
def create_new_user(user: UserCreate, user_service:UserService = Depends(get_user_service)):
    result = user_service.create_user(User.model_validate(user))
    
    return result

@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: str, user: UserUpdate, user_service:UserService = Depends(get_user_service)):
    result = user_service.update_user(
        user_id, 
        user.model_dump(exclude_unset=True)
    )
    
    return result

@router.post("/create_table")
def create_user_table(
    db:Session=Depends(get_db),
    schema:str = Query(description="Schema database", default="C##FARID")
    ):
    try:
        create_table(db, engine, User, "users_id_seq", schema)
        
        return {"message": "User table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create table fails!\n{str(e)}")

@router.delete("/drop_table")
def drop_user_table(
    db:Session=Depends(get_db),
    schema:str = Query(description="Schema database", default="C##FARID")
    ):
    try:
        drop_table(db, engine, User, "users_id_seq", schema)
        
        return {"message": "User table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drop table fails!\n{str(e)}")