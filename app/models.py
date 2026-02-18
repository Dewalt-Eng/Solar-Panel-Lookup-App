import uuid
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
import secrets


def generate_reference_code():
    date_part = datetime.utcnow().strftime("%Y%m%d")
    hex_part = secrets.token_hex(4).upper()  # 8 hex chars
    return f"{date_part}-{hex_part}"

class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    internal_code = Column(String, unique=True, nullable=False, index=True)
    reference_code = Column(String, unique=True, index=True, default=generate_reference_code)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)

    tests = relationship(
        "PanelTest",
        back_populates="item",
        cascade="all, delete"
    )


class PanelTest(Base):
    __tablename__ = "panel_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False
    )

    test_date = Column(Date, nullable=True)
    tested_by = Column(String, nullable=True)
    result = Column(String, nullable=True)

    item = relationship(
        "Item",
        back_populates="tests"
    )


