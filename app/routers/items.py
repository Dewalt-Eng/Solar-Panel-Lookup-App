from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app import models, schemas
from app.services.report_service import get_items_with_tests
from app.services.lookup_service import get_item_with_latest_test
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
import os
from app.services.qr_service import generate_qr_image


templates = Jinja2Templates(directory="app/templates")


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
def download_item_qr(internal_code: str, db: Session = Depends(get_db)):

    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")

    lookup_url = f"{base_url}/items/lookup-view?serial={internal_code}"

    image_buffer = generate_qr_image(lookup_url)

    # Optional: use reference_code as filename
    item = db.query(models.Item).filter_by(
        internal_code=internal_code
    ).first()

    filename = item.reference_code if item else internal_code

    return StreamingResponse(
        image_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.png"
        }
    )


@router.get("/lookup-view")
def lookup_view(
    serial: str,
    request: Request,
    db: Session = Depends(get_db)
):

    # Find item by internal serial
    item = db.query(models.Item).filter_by(
        internal_code=serial
    ).first()

    if not item:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "error": "Item not found"
            }
        )

    # Get latest test
    latest_test = (
        db.query(models.PanelTest)
        .filter_by(item_id=item.id)
        .order_by(models.PanelTest.test_date.desc())
        .first()
    )

    return templates.TemplateResponse(
        "lookup.html",
        {
            "request": request,
            "item": item,
            "test": latest_test
        }
    )


@router.get("/all")
def view_all_items(request: Request, db: Session = Depends(get_db)):

    items = db.query(models.Item).order_by(models.Item.internal_code).all()

    return templates.TemplateResponse(
        "items_list.html",
        {
            "request": request,
            "items": items
        }
    )
    
