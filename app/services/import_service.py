#imports used for the code responsible for implementing upload functionalities
import pandas as pd
from app import models
from datetime import datetime

#help ensure clean serial_number imported
def clean_serial(value):
    return (
        str(value)
        .strip()
        .replace("'", "")
        .replace('"', "")
        .replace(" ", "")
    )

#help ensure clean float values imported
def safe_float(value):
    try:
        if value in [None, "", "nan"]:
            return None
        return float(value)
    except:
        return None

#help ensure clean integer values imported
def safe_int(value):
    try:
        if value in [None, "", "nan"]:
            return None
        return int(float(value))
    except:
        return None

#help ensure clean string values imported
def safe_str(value):
    if value in [None, "", "nan"]:
        return None
    return str(value).strip()

#function responsible for the import 
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
        
        ###################################
        # ---------- ITEM UPSERT ----------
        ###################################
        
        item = db.query(models.Item).filter_by(
            internal_code=serial
        ).first()

        if not item:
            item = models.Item(
                internal_code=serial,
                name=safe_str(row.get("model")),
                category=safe_str(row.get("unit_type")),
                manufacturer=safe_str(row.get("manufacturer")),
                length=safe_float(row.get("length")),
                width=safe_float(row.get("width")),
                thickness=safe_float(row.get("thickness")),
                area=safe_float(row.get("area")),
                number_of_cells=safe_int(row.get("number_of_cells")),
                junction_box_ip_rating=safe_str(row.get("junction_box_ip_rating")),
                new_serial_number=safe_str(row.get("new_serial_number"))
            )
            db.add(item)
            db.flush()
            inserted_items += 1
        else:
            # Update item fields
            item.name = safe_str(row.get("model"))
            item.category = safe_str(row.get("unit_type"))
            item.manufacturer = safe_str(row.get("manufacturer"))
            item.length = safe_float(row.get("length"))
            item.width = safe_float(row.get("width"))
            item.thickness = safe_float(row.get("thickness"))
            item.area = safe_float(row.get("area"))
            item.number_of_cells = safe_int(row.get("number_of_cells"))
            item.junction_box_ip_rating = safe_str(row.get("junction_box_ip_rating"))
            item.new_serial_number = safe_str(row.get("new_serial_number"))
            updated_items += 1

        ###################################
        # ---------- TEST UPSERT ----------
        ###################################

        test_date_raw = row.get("test_date")
        if not test_date_raw:
            continue

        test_date = pd.to_datetime(test_date_raw, errors="coerce")
        if pd.isna(test_date):
            continue

        test_date = test_date.date()

        test = db.query(models.PanelTest).filter_by(
            item_id=item.id,
            test_date=test_date
        ).first()

        tested_by = safe_str(row.get("tested_by"))
        result = safe_str(row.get("result"))

        if not test:
            test = models.PanelTest(
                item_id=item.id,
                test_date=test_date,
                tested_by=tested_by,
                result=result,
                solution_resistivity=safe_float(row.get("solution_resistivity")),
                solution_temp=safe_float(row.get("solution_temp")),
                voltage_applied=safe_float(row.get("voltage_applied")),
                insulation_resistance=safe_float(row.get("insulation_resistance")),
                pass_fail_threshold=safe_float(row.get("pass_fail_threshold"))
            )
            db.add(test)
            inserted_tests += 1
        else:
            test.tested_by = tested_by
            test.result = result
            test.solution_resistivity = safe_float(row.get("solution_resistivity"))
            test.solution_temp = safe_float(row.get("solution_temp"))
            test.voltage_applied = safe_float(row.get("voltage_applied"))
            test.insulation_resistance = safe_float(row.get("insulation_resistance"))
            test.pass_fail_threshold = safe_float(row.get("pass_fail_threshold"))
            updated_tests += 1

    db.commit()

    return inserted_items, updated_items, inserted_tests, updated_tests