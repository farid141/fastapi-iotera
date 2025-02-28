from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, Sequence, insert
from typing import Annotated

from app.db.session import get_db, engine
from app.db.utils import create_sequence, drop_sequence, inspect_table
from app.db.models.item import ItemCreate, ItemRead, Item, ItemUpdate
from app.db.models.user import User

router = APIRouter()

@router.post("/")
def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item.model_validate(item).__dict__

    last_seq = db.exec(select(Item).order_by(Item.seq_id.desc()).limit(1)).first()
    last_seq = 0 if last_seq is None else last_seq.seq_id
    last_seq+=1

    dict_item = {
        "seq_id": last_seq,
        "id": F"TEST_{last_seq}",
        "owner_id": db_item["owner_id"],
        "name": db_item["name"],
        "description": db_item["description"],
    }

    db.exec(insert(Item).values(dict_item))
    db.commit()
    return dict_item

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