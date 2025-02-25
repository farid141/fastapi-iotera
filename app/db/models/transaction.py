from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class TransactionBase(SQLModel):
    device_id:str
    product_name:str
    product_price:float
    product_quantity:int
    amount:float
    fee:float
    nett:float
    transaction_status:str
    payment_status:str
    payment_method:str
    firebase_timestamp:datetime

class Transaction(TransactionBase, table=True):  # Table model
    __tablename__ = "transactions"  # Explicitly set the table name
    uuid: Optional[str] = Field(default=None, primary_key=True)

class TransactionRead(TransactionBase):  # Schema for reading a transaction
    uuid: str
