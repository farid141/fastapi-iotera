from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Annotated

from app.db.session import get_db, engine
from app.db.utils import create_sequence, drop_sequence, inspect_table
from app.db.models.item import ItemCreate, ItemRead, Item, ItemUpdate
from app.db.models.user import User

router = APIRouter()

@router.post("/", response_model=ItemRead)
def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    statement = select(Item, User).where(Item.id == item_id).join(User, isouter=True)
    item, user = db.exec(statement).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/", response_model=list[ItemRead])
def get_item(
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    ):
    statement = select(Item).offset(offset).limit(limit)
    results = db.exec(statement).all()

    if not results:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return results

@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemUpdate, db:Session=Depends(get_db)):
    item_db = db.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_data = item.model_dump(exclude_unset=True) # mengekstrak field kosong dan default value dari request body
    item_db.sqlmodel_update(item_data)  # validasi field ke table model
    db.add(item_db)
    db.commit()
    db.refresh(item_db)
    return item_db
    
@router.post("/create_table")
def create_item_table(db:Session=Depends(get_db)):
    try:
        if inspect_table(Item.__tablename__):
            raise Exception("Table already exists!")

        create_sequence(db, "items_id_seq")
        Item.metadata.create_all(engine, [Item.__table__], False)
        
        return {"message": "Item table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create table fails!\n{str(e)}")

@router.delete("/drop_table")
def drop_item_table(db:Session=Depends(get_db)):
    try:
        if not inspect_table(Item.__tablename__):
            raise Exception("Table doesn't exists!")

        drop_sequence(db, "items_id_seq")
        Item.metadata.drop_all(engine, [Item.__table__], False)
        
        return {"message": "Item table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drop table fails!\n{str(e)}")