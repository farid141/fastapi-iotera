from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func
from typing import Annotated
from datetime import datetime
import requests

from app.db.session import get_db, engine
from app.db.utils import create_table, drop_table
from app.auth.dependencies import get_current_user
from app.services.transaction import TransactionService
from app.db.repositories.transaction import TransactionRepository
from app.db.models.transaction import Transaction, TransactionRead, TransactionCreate
from app.db.enum import DeviceIdsEnum, PaymentStatusesEnum, TransactionStatusesEnum, PaymentMethodEnum

router = APIRouter()

def get_transaction_service(session: Session = Depends(get_db))->TransactionService:
    transaction_repository = TransactionRepository(session)
    return TransactionService(transaction_repository)

@router.post("/", response_model=TransactionRead)
def create_transaction(
    transaction: TransactionCreate, 
    transaction_service:TransactionService = Depends(get_transaction_service),
    schema:str = Query(description="Schema database", default="C##FARID")
    ):
    result = transaction_service.create_transaction(schema, Transaction.model_validate(transaction))
    
    return result

@router.get("/", response_model=list[TransactionRead])
def get_transaction(
    transaction_service:TransactionService = Depends(get_transaction_service),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    ):
    results = transaction_service.get_transactions(limit, offset)

    if not results:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return results

@router.get("/count_and_amount_by_status")
def count_and_amount_by_status(
    device_id: DeviceIdsEnum|None= Query(default=None,description="Choose a device id"), # type:ignore
    payment_status: PaymentStatusesEnum|None= Query(default=None,description="Choose a payment status"), # type:ignore
    transaction_status: TransactionStatusesEnum|None= Query(default=None,description="Choose a transaction status"), # type:ignore
    payment_method: PaymentMethodEnum|None= Query(default=None,description="Choose a payment method"), # type:ignore
    session: Session = Depends(get_db)
    ):
    
    stmt = select(Transaction.transaction_status, 
                  func.count().label("count"), 
                  func.sum(Transaction.amount).label("amount"))
    stmt = stmt.group_by(Transaction.transaction_status)

    if device_id:
        stmt = stmt.where(Transaction.device_id == device_id.value)
    if payment_status:
        stmt = stmt.where(Transaction.payment_status == payment_status.value)
    if transaction_status:
        stmt = stmt.where(Transaction.transaction_status == transaction_status.value)
    if payment_method:
        stmt = stmt.where(Transaction.payment_method == payment_method.value)

    results = session.exec(stmt).all()
    return sorted([r._asdict() for r in results], key=lambda x: x['amount'], reverse=True)

@router.get("/amount_by_month")
def amount_by_month(session: Session = Depends(get_db)):
    stmt = select(func.strftime('%Y-%m', Transaction.firebase_timestamp).label("month"),
                  func.sum(Transaction.amount).label("amount"))
    stmt = stmt.group_by("month")
    results = session.exec(stmt).all()
    return {r.month: r.amount for r in results}

@router.get("/qty_and_amount_by_product")
def qty_and_amount_by_product(session: Session = Depends(get_db)):
    stmt = select(Transaction.product_name, 
                  func.count().label("transaction_count"),
                  func.sum(Transaction.product_quantity).label("qty"),
                  func.sum(Transaction.amount).label("amount"))
    stmt = stmt.group_by(Transaction.product_name)
    results = session.exec(stmt).all()
    return sorted([r._asdict() for r in results], key=lambda x: x['amount'], reverse=True)

@router.get("/payment_method_and_status_by_payment")
def payment_method_and_status_by_payment(session: Session = Depends(get_db), current_user:dict = Depends(get_current_user)):
    transactions = session.exec(select(Transaction)).all()
    data = {}

    for trx in transactions:
        if trx.payment_method not in data:
            data[trx.payment_method] = {"count": 0, "payment_status": {}}
        
        data[trx.payment_method]["count"] += 1

        if trx.payment_status not in data[trx.payment_method]["payment_status"]:
            data[trx.payment_method]["payment_status"][trx.payment_status] = 0

        data[trx.payment_method]["payment_status"][trx.payment_status] += 1

    # Mengurutkan berdasarkan jumlah transaksi
    sorted_data = sorted(
        [{**{"payment_method": k}, **v, "payment_status": dict(sorted(v["payment_status"].items(), key=lambda x: x[1], reverse=True))} for k, v in data.items()], 
        key=lambda x: x['count'], 
        reverse=True
    )

    return sorted_data
                    
@router.post("/sync_data")
def sync_data(session: Session = Depends(get_db)):
    # Request to the API
    response = requests.post(
        "https://login-bir3msoyja-et.a.run.app",
        json={"user": "user", "password": "password"}
    )

    data_response = response.json().get("data", {})

    # Process each transaction
    to_insert = []
    for key, data in data_response.items():
        try:
            timestamp = datetime.utcfromtimestamp(data['time']['firestore_timestamp']['_seconds'])
            fee = data['payment']['amount'] - data['payment']['nett']
            
            transaction = Transaction(
                uuid=key,
                device_id=data.get('product', {}).get('device_id', '-') or '-',
                product_name=data.get('product', {}).get('name', '-') or '-',
                product_price=data.get('product', {}).get('price', 0) or 0,
                product_quantity=data.get('product', {}).get('quantity', 0) or 0,
                amount=data['payment']['amount'],
                fee=fee,
                nett=data['payment']['nett'],
                transaction_status=data.get('detail', {}).get('transaction_status', '-') or '-',
                payment_status=data.get('payment', {}).get('detail', {}).get('transaction_status', '-') or '-',
                payment_method=data.get('payment', {}).get('method', '-') or '-',
                firebase_timestamp=timestamp,
            )
            to_insert.append(transaction)
        except Exception as e:
            print(f"Sync error: {e}")

    # Insert transactions into the database
    session.add_all(to_insert)
    session.commit()

@router.post("/create_table")
def create_transaction_table(
    db: Session = Depends(get_db), 
    schema:str = Query(description="Schema database", default="C##FARID")
    ):
    try:
        create_table(db, engine, Transaction, None, schema)
        
        return {"message": "Transaction table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create table fails!\n{str(e)}")
    
@router.delete("/drop_table")
def drop_transaction_table(
    db: Session = Depends(get_db),
    schema:str = Query(description="Schema database", default="C##FARID")
    ):
    try:
        drop_table(db, engine, Transaction, None, schema)
        
        return {"message": "Transaction table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drop table fails!\n{str(e)}")