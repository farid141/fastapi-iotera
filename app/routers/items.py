from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_db, engine
from app.db.models.item import ItemCreate, ItemRead, Item
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

@router.post("/create_table")
def create_item_table(db: Session = Depends(get_db)):
    try:
        Item.metadata.create_all(engine, [Item.__table__], False)
        
        return {"message": "Item table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Item table already exists!")

@router.post("/drop_table")
def drop_item_table(db: Session = Depends(get_db)):
    try:
        Item.metadata.drop_all(engine, [Item.__table__], False)
        
        return {"message": "Item table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Item table doesn't exists")