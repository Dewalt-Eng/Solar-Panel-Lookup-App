#This code is responsible for the implementation for the web apps endpoints

#All of the imports used for the endpoints of the web app
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
import io
import zipfile

templates = Jinja2Templates(directory="app/templates")

#provides the chosen "items" path and tags to the route operations w.r.t the lookup endpoints
router = APIRouter(prefix="/items", tags=["Items"])

###############################################################
#IMPORTANT NOTE: 
# NOT ALL ENDPOINTS ARE NOT IN ACTIVE USE IN THE DEPLOYED CODE W.R.T THE UI ACCESSABILITY
# MANY ENDPOINTS ARE USED FOR DEVELOPMENT, DEBUGGING AND TESTING PURPOSES
# COMMENTS WILL BE USED TO EXPLAIN THE NATURE OF EACH ENDPOINT 
###############################################################


#this is the endpoint used to create an panel entry and store is in the database based on the defined schema
@router.post("/", response_model=schemas.ItemResponse)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):

    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

#this is the endpoint used to create an panel test entry and store is in the database based on the defined schema
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

#This was a testing/debugging used to ensure that data could be retrieved from the database
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

#This is the debugging endpoint used for testing a serial_number based lookup on the stored entries of panels
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

#The is the endpoint for the QR image file generated based on the encoded serial_number endpoint
@router.get("/{internal_code}/qr")
def get_item_qr(internal_code: str):

    base_url = os.getenv("BASE_URL")
    #lookup_url = f"{base_url}/items/lookup/{internal_code}"
    lookup_url = f"{base_url}/items/lookup-view?serial={internal_code}"

    image_buffer = generate_qr_image(lookup_url)

    return StreamingResponse(
        image_buffer,
        media_type="image/png"
    )
    

#The is the endpoint for downloading the generated QR image based on the provided serial_number
@router.get("/{internal_code}/qr/download")
def download_item_qr(internal_code: str, db: Session = Depends(get_db)):

    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")

    lookup_url = f"{base_url}/items/lookup-view?serial={internal_code}"

    image_buffer = generate_qr_image(lookup_url)

    # Optional: use reference_code as filename
    item = db.query(models.Item).filter_by(
        internal_code=internal_code
    ).first()

    #filename = item.new_serial_number if item else internal_code 
    filename = internal_code 

    return StreamingResponse(
        image_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.png"
        }
    )

#This is the endpoint used for the generating, zipping and downloading of all generated QR images based on the entries stored
@router.get("/qr/download-all")
def download_all_qr(db: Session = Depends(get_db)):

    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")

    items = db.query(models.Item).all()

    # Create in-memory zip buffer
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        for item in items:

            lookup_url = f"{base_url}/items/lookup-view?serial={item.internal_code}"

            image_buffer = generate_qr_image(lookup_url)

            # Use reference_code for filename if available
            filename =item.internal_code or item.new_serial_number
            zip_file.writestr(f"{filename}.png", image_buffer.getvalue())

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=all_qr_codes.zip"
        }
    )

#This is the lookup endpoint used for making a serial_number based lookup on the stored entries of panels
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

#This is the testing endpoint used for displaying all the stored entries of panels that are stored in the database
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

#This a debugging and testing endpoint used to determine whether the database is working and storing the data
@router.get("/debug-count")
def debug_count(db: Session = Depends(get_db)):
    return {
        "item_count": db.query(models.Item).count()
    }    
