import pandas as pd
from app import models
from datetime import datetime

def clean_serial(value):
    return (
        str(value)
        .strip()
        .replace("'", "")
        .replace('"', "")
        .replace(" ", "")
    )

def import_master_sheet(db, file_path: str):

    df = pd.read_excel(file_path, dtype=str)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    inserted_items = 0
    updated_items = 0
    inserted_tests = 0
    updated_tests = 0

    for _, row in df.iterrows():

        serial = row.get("serial_number")

        if not serial:
            continue

        serial = str(serial).strip()

        # ---------- ITEM UPSERT ----------
        item = db.query(models.Item).filter_by(
            internal_code=serial
        ).first()

        if not item:
            item = models.Item(
                internal_code=serial,
                name=str(row.get("model") or "").strip(),
                category=str(row.get("unit_type") or "").strip()
            )
            db.add(item)
            db.flush()
            inserted_items += 1
        else:
            # Update fields if changed
            new_name = str(row.get("model") or "").strip()
            new_category = str(row.get("unit_type") or "").strip()

            if item.name != new_name or item.category != new_category:
                item.name = new_name
                item.category = new_category
                updated_items += 1

        # ---------- TEST UPSERT ----------
        new_tested_by = str(row.get("tested_by") or "").strip()
        new_result = str(row.get("result") or "").strip()

        test_date_raw = row.get("test_date")

        if not test_date_raw:
            continue

        # Convert safely
        test_date = pd.to_datetime(test_date_raw, errors="coerce")

        # Skip invalid / empty dates
        if pd.isna(test_date):
            continue

        test_date = test_date.date()

        test = db.query(models.PanelTest).filter_by(
            item_id=item.id,
            test_date=test_date
        ).first()

        new_tested_by = (row.get("tested_by") or "").strip()
        new_result = (row.get("result") or "").strip()

        if not test:
            test = models.PanelTest(
                item_id=item.id,
                test_date=test_date,
                tested_by=new_tested_by,
                result=new_result
            )
            db.add(test)
            inserted_tests += 1
        else:
            if (
                test.tested_by != new_tested_by or
                test.result != new_result
            ):
                test.tested_by = new_tested_by
                test.result = new_result
                updated_tests += 1

    db.commit()

    return inserted_items, updated_items, inserted_tests, updated_tests