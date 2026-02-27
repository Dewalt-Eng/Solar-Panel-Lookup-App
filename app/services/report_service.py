from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models


def get_items_with_tests(db: Session):

    stmt = (
        select(
            models.Item.id,
            models.Item.internal_code,
            models.Item.name,
            models.Item.manufacturer,
            models.PanelTest.test_date,
            models.PanelTest.tested_by,
            models.PanelTest.result
        )
        .outerjoin(
            models.PanelTest,
            models.Item.id == models.PanelTest.item_id
        )
    )

    result = db.execute(stmt)

    return result.all()
