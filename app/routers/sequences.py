from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Annotated

from app.db.session import get_db, engine
from app.db.utils import inspect_table
from ..db.models.sequence import Sequence

router = APIRouter()

@router.post("/create_table")
def create_sequence_table(db:Session=Depends(get_db)):
    try:
        if inspect_table(Sequence.__tablename__):
            raise Exception("Table already exists!")
        Sequence.metadata.create_all(engine, [Sequence.__table__], False)
        
        return {"message": "Sequence table created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create table fails!\n{str(e)}")

@router.delete("/drop_table")
def drop_sequence_table(db:Session=Depends(get_db)):
    try:
        if not inspect_table(Sequence.__tablename__):
            raise Exception("Table doesn't exists!")
        Sequence.metadata.drop_all(engine, [Sequence.__table__], False)
        
        return {"message": "Sequence table dropped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drop table fails!\n{str(e)}")