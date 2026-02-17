from pydantic import BaseModel
from uuid import UUID
from datetime import date


class ItemCreate(BaseModel):
    internal_code: str
    name: str
    category: str

class ItemResponse(ItemCreate):
    id: UUID

    class Config:
        from_attributes = True

class PanelTestCreate(BaseModel):
    internal_code: str
    test_date: date
    tested_by: str
    result: str

class PanelTestResponse(BaseModel):
    id: UUID
    test_date: date
    tested_by: str
    result: str

    class Config:
        from_attributes = True
