import pandas as pd
from app import models
from datetime import datetime


def import_items(db, file_path: str):

    df = pd.read_excel(file_path, dtype=str)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():

        serial = clean_serial(row["serial_number"])

        existing = db.query(models.Item).filter_by(
            internal_code=serial
        ).first()

        if existing:
            skipped += 1
            continue

        item = models.Item(
            internal_code=serial,
            name=str(row.get("model", "")).strip(),
            category=str(row.get("unit_type", "")).strip()
        )

        db.add(item)
        inserted += 1

    db.commit()

    print(f"Items inserted: {inserted}")
    print(f"Items skipped: {skipped}")



def import_panel_tests(db, file_path: str):

    df = pd.read_excel(file_path)

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    inserted = 0
    skipped = 0

    failed_rows = []

    for _, row in df.iterrows():

        serial = clean_serial(row["serial_number"])

        item = db.query(models.Item).filter_by(
            internal_code=serial
        ).first()

        if not item:
            failed_rows.append({
                "serial_number": serial,
                "reason": "Item not found"
            })
            skipped += 1
            continue

        if pd.isna(row["test_date"]):
            failed_rows.append({
                "serial_number": serial,
                "reason": "Missing test_date"
            })
            skipped += 1
            continue

        test_date = pd.to_datetime(row["test_date"]).date()

        test = models.PanelTest(
            item_id=item.id,
            test_date=test_date,
            tested_by=str(row.get("tested_by", "")).strip(),
            result=str(row.get("result", "")).strip()
        )

        db.add(test)
        inserted += 1

    db.commit()

    # Export failed rows if any
    #if failed_rows:
        #failed_df = pd.DataFrame(failed_rows)

        #output_path = "data/failed_tests_import.csv"

        # Ensure data folder exists
        #import os
        #os.makedirs("data", exist_ok=True)
        #failed_df.to_csv(output_path, index=False)

        #print(f"Failed rows exported to {output_path}")

    print(f"Tests inserted: {inserted}")
    print(f"Tests skipped: {skipped}")

def clean_serial(value):
    return (
        str(value)
        .strip()
        .replace("'", "")
        .replace('"', "")
        .replace(" ", "")
    )

