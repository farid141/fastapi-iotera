from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class TransactionBase(SQLModel):
    device_id:str = Field(max_length=50)
    product_name:str = Field(max_length=50)
    product_price:float
    product_quantity:int
    amount:float
    fee:float
    nett:float
    transaction_status:str = Field(max_length=50)
    payment_status:str = Field(max_length=50)
    payment_method:str = Field(max_length=50)
    firebase_timestamp:datetime

class Transaction(TransactionBase, table=True):  # Table model
    __tablename__ = "transactions"  # Explicitly set the table name
    uuid: Optional[str] = Field(default=None, primary_key=True, max_length=50)

class TransactionRead(TransactionBase):  # Schema for reading a transaction
    uuid: str