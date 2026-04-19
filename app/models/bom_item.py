from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BomItem(Base):
    __tablename__ = "bom_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bom_id: Mapped[int] = mapped_column(
        ForeignKey("bom.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    parent_item_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("bom_item.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True
    )
    child_part_id: Mapped[int] = mapped_column(
        ForeignKey("part.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    item_name_snapshot: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    item_number_snapshot: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    item_version_snapshot: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, server_default=text("1"))
    quantity_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("unit.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    is_outsourced: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    sort_no: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    remark: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    bom = relationship("Bom", back_populates="items")
    parent_item = relationship("BomItem", remote_side=[id], back_populates="children")
    children = relationship("BomItem", back_populates="parent_item", cascade="all, delete-orphan")
    child_part = relationship("Part")
    quantity_unit = relationship("Unit")

    @property
    def child_part_code(self) -> Optional[str]:
        if self.child_part is None:
            return None
        return self.child_part.part_code

    @property
    def child_part_name(self) -> Optional[str]:
        if self.child_part is None:
            return None
        return self.child_part.part_name

    @property
    def quantity_unit_name(self) -> Optional[str]:
        if self.quantity_unit is None:
            return None
        return self.quantity_unit.unit_name

