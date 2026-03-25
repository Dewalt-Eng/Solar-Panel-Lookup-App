#Imports used for the code describing the schemas of endpoints
from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional

####################################
# ---------- ITEM SCHEMAS ----------
####################################
class ItemCreate(BaseModel):
    internal_code: str
    name: Optional[str] = None
    category: Optional[str] = None

    length: Optional[float] = None
    width: Optional[float] = None
    thickness: Optional[float] = None
    area: Optional[float] = None
    number_of_cells: Optional[int] = None
    junction_box_ip_rating: Optional[str] = None
    new_serial_number: Optional[str] = None


class ItemResponse(ItemCreate):
    id: UUID
    reference_code: str
    new_serial_number: Optional[str] = None

    class Config:
        from_attributes = True

##############################################
# ---------- PANEL TESTING SCHEMAS ----------
##############################################

class PanelTestCreate(BaseModel):
    internal_code: str
    test_date: date
    tested_by: Optional[str] = None
    result: Optional[str] = None

    solution_resistivity: Optional[float] = None
    solution_temp: Optional[float] = None
    voltage_applied: Optional[float] = None
    insulation_resistance: Optional[float] = None
    pass_fail_threshold: Optional[float] = None
    


class PanelTestResponse(BaseModel):
    id: UUID
    test_date: date
    tested_by: Optional[str] = None
    result: Optional[str] = None

    solution_resistivity: Optional[float] = None
    solution_temp: Optional[float] = None
    voltage_applied: Optional[float] = None
    insulation_resistance: Optional[float] = None
    pass_fail_threshold: Optional[float] = None

    class Config:
        from_attributes = True