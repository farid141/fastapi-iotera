from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Annotated

from app.db.session import get_db, engine
from app.db.utils import create_table, drop_table
from app.db.models.item import ItemCreate, ItemRead, Item, ItemUpdate

from app.services.item import ItemService
from app.db.repositories.item import ItemRepository

router = APIRouter()

def get_item_service(session: Session = Depends(get_db))->ItemService:
    item_repository = ItemRepository(session)
    return ItemService(item_repository)

@router.get("/", response_model=list[ItemRead])
def get_item(
    item_service:ItemService = Depends(get_item_service),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    ):
    results = item_service.get_items(limit, offset)

    if not results:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return results

@router.get("/{item_id}", response_model=ItemRead)
def read_item(item_id: str, item_service:ItemService = Depends(get_item_service)):
    item = item_service.get_item_by_id(item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemRead)
def create_new_item(item: ItemCreate, item_service:ItemService = Depends(get_item_service)):
    result = item_service.create_item(Item.model_validate(item))

    return result

@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: str, item: ItemUpdate, item_service:ItemService = Depends(get_item_service)):
    result = item_service.update_item(
        item_id, 
        item.model_dump(exclude_unset=True)
    )
    
    return result
    
@router.post("/create_table")
def create_item_table(
    db:Session=Depends(get_db),
    schema:str = Query(description="Schema database", default="C##FARID")
    ):
    try:
        create_table(db, engine, Item, "items_id_seq", schema)
        
        return {"message": "Item table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create table fails!\n{str(e)}")

@router.delete("/drop_table")
def drop_item_table(
    db:Session=Depends(get_db),
    schema:str = Query(description="Schema database", default="C##FARID")
    ):
    try:
        drop_table(db, engine, Item, "items_id_seq", schema)

        return {"message": "Item table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drop table fails!\n{str(e)}")