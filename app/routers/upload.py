from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.import_service import import_master_sheet
import shutil
import os
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/import")
def upload_master_sheet(file: UploadFile = File(...), db: Session = Depends(get_db)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        inserted_i, updated_i, inserted_t, updated_t = import_master_sheet(db, temp_path)

        message = (
            f"import_success"
            f"&new_items={inserted_i}"
            f"&updated_items={updated_i}"
            f"&new_tests={inserted_t}"
            f"&updated_tests={updated_t}"
        )
    except Exception as e:
        print("IMPORT ERROR:", e)
        message = "import_error"

    os.remove(temp_path)

    return RedirectResponse(
        url=f"/?status={message}",
        status_code=303
    )
    