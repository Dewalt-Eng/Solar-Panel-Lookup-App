#imports used for the lookup service implementation
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app import models

#this code is used to extract the latest panel test results from the looked up database entry
def get_item_with_latest_test(db: Session, internal_code: str):

    # Get item
    item = db.query(models.Item).filter_by(
        internal_code=internal_code
    ).first()

    if not item:
        return None

    # Get latest test (if any)
    latest_test = (
        db.query(models.PanelTest)
        .filter_by(item_id=item.id)
        .order_by(desc(models.PanelTest.test_date))
        .first()
    )

    return item, latest_test
