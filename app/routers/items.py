from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas
from app.services.report_service import get_items_with_tests
from app.services.lookup_service import get_item_with_latest_test
from fastapi.responses import StreamingResponse
import os
from app.services.qr_service import generate_qr_image


router = APIRouter(prefix="/items", tags=["Items"])

@router.post("/", response_model=schemas.ItemResponse)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):

    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@router.post("/test")
def add_test(test: schemas.PanelTestCreate, db: Session = Depends(get_db)):

    item = db.query(models.Item).filter_by(
        internal_code=test.internal_code
    ).first()

    if not item:
        return {"error": "Item not found"}

    panel_test = models.PanelTest(
        item_id=item.id,
        test_date=test.test_date,
        tested_by=test.tested_by,
        result=test.result
    )

    db.add(panel_test)
    db.commit()

    return {"message": "Test added"}

@router.get("/report")
def items_report(db: Session = Depends(get_db)):

    rows = get_items_with_tests(db)

    return [
        {
            "id": row.id,
            "internal_code": row.internal_code,
            "name": row.name,
            "category": row.category,
            "test_date": row.test_date,
            "tested_by": row.tested_by,
            "result": row.result
        }
        for row in rows
    ]

@router.get("/lookup/{internal_code}")
def lookup_item(internal_code: str, db: Session = Depends(get_db)):

    result = get_item_with_latest_test(db, internal_code)

    if not result:
        return {"error": "Item not found"}

    item, latest_test = result

    return {
        "internal_code": item.internal_code,
        "name": item.name,
        "category": item.category,
        "latest_test": {
            "test_date": latest_test.test_date if latest_test else None,
            "tested_by": latest_test.tested_by if latest_test else None,
            "result": latest_test.result if latest_test else None
        }
    }

@router.get("/{internal_code}/qr")
def get_item_qr(internal_code: str):

    base_url = os.getenv("BASE_URL")
    lookup_url = f"{base_url}/items/lookup/{internal_code}"

    image_buffer = generate_qr_image(lookup_url)

    return StreamingResponse(
        image_buffer,
        media_type="image/png"
    )
    

@router.get("/{internal_code}/qr/download")
def download_item_qr(internal_code: str):

    base_url = os.getenv("BASE_URL")
    lookup_url = f"{base_url}/items/lookup/{internal_code}"

    image_buffer = generate_qr_image(lookup_url)

    return StreamingResponse(
        image_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename={internal_code}.png"
        }
    )

    
