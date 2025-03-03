from sqlmodel import select, Session
from fastapi import HTTPException

from app.db.models.user import User, UserUpdate
from app.db.utils import next_sequence, create_sequence, drop_sequence, inspect_table

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_users(self, limit: int = 10, offset: int = 0) -> list[User]:
        query = select(User).offset(offset).limit(limit)
        return self.session.exec(query).all()
    
    def get_user_by_id(self, user_id: int)->User:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first()
    
    def create_user(self, db_user: User)->User:
        db_user.id = next_sequence(
            db=self.session,
            prefix="USR",
            sequence_name='users_id_seq'
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user
    
    def update_user(self, user_id:int, update_data:dict)->User:
        user_db = self.session.get(User, user_id)
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_db.sqlmodel_update(update_data)
        self.session.add(user_db)
        self.session.commit()
        self.session.refresh(user_db)

        return user_db
