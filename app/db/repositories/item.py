from sqlmodel import select, Session
from fastapi import HTTPException

from app.db.models.item import Item, ItemUpdate
from app.db.utils import next_sequence

class ItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_items(self, limit: int = 10, offset: int = 0) -> list[Item]:
        query = select(Item).offset(offset).limit(limit)
        return self.session.exec(query).all()
    
    def get_item_by_id(self, item_id: int)->Item:
        statement = select(Item).where(Item.id == item_id)
        return self.session.exec(statement).first()
    
    def create_item(self, db_item: Item)->Item:
        db_item.id = next_sequence(
            db=self.session,
            prefix="ITM",
            sequence_name='items_id_seq'
        )
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item
    
    def update_item(self, item_id:int, update_data:dict)->Item:
        item_db = self.session.get(Item, item_id)
        if not item_db:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item_db.sqlmodel_update(update_data)
        self.session.add(item_db)
        self.session.commit()
        self.session.refresh(item_db)

        return item_db
