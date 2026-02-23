from app.db import SessionLocal, engine
from app import models
from app.services.import_service import import_master_sheet

# Create tables if they don’t exist
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Use your new master sheet
inserted_i, updated_i, inserted_t, updated_t = import_master_sheet(
    db,
    "solar_data_cleaned.xlsx"
)

db.close()

print("Seeding complete.")
print(f"New items: {inserted_i}")
print(f"Updated items: {updated_i}")
print(f"New tests: {inserted_t}")
print(f"Updated tests: {updated_t}")
