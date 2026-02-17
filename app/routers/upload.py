from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.import_service import import_items, import_panel_tests
import shutil
import os

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/solar")
def upload_solar(file: UploadFile = File(...), db: Session = Depends(get_db)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    import_items(db, temp_path)

    os.remove(temp_path)

    return {"message": "Solar units imported"}


@router.post("/tests")
def upload_tests(file: UploadFile = File(...), db: Session = Depends(get_db)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    import_panel_tests(db, temp_path)

    os.remove(temp_path)

    return {"message": "Panel tests imported"}
