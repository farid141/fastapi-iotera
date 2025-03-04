from sqlmodel import select, Session
from fastapi import HTTPException
import time

from app.db.models.transaction import Transaction

class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_transactions(self, limit: int = 10, offset: int = 0) -> list[Transaction]:
        query = select(Transaction).offset(offset).limit(limit)
        return self.session.exec(query).all()
    
    def get_transaction_by_id(self, transaction_id: int)->Transaction:
        statement = select(Transaction).where(Transaction.id == transaction_id)
        return self.session.exec(statement).first()
    
    def create_transaction(self, prefix, db_transaction: Transaction)->Transaction:
        db_transaction.uuid = f"{prefix}-{int(time.time() * 1000)}"
        self.session.add(db_transaction)
        self.session.commit()
        self.session.refresh(db_transaction)
        return db_transaction
