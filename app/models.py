import uuid
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base




class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    internal_code = Column(String, unique=True, nullable=False, index=True)
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

