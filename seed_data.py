from app.db import SessionLocal, engine
from app import models
from app.services.import_service import import_items, import_panel_tests

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

import_items(db, "solar_units.xlsx")
import_panel_tests(db, "test_panels.xlsx")

db.close()

print("Seeding complete.")
