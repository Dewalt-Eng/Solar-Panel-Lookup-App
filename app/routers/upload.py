from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.import_service import import_items, import_panel_tests
import shutil
import os
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/solar")
def upload_solar(file: UploadFile = File(...), db: Session = Depends(get_db)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        import_items(db, temp_path)
        message = "solar_success"
    except Exception:
        message = "solar_error"

    os.remove(temp_path)

    return RedirectResponse(
        url=f"/?status={message}",
        status_code=303
    )



@router.post("/tests")
def upload_tests(file: UploadFile = File(...), db: Session = Depends(get_db)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        import_panel_tests(db, temp_path)
        message = "tests_success"
    except Exception:
        message = "tests_error"

    os.remove(temp_path)

    return RedirectResponse(
        url=f"/?status={message}",
        status_code=303
    )

