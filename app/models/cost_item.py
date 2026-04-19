from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CostItem(Base):
    __tablename__ = "cost_item"

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    calculation_name: Mapped[str] = mapped_column(String(128), nullable=False)
    part_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("part.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    currency_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("currency.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    unit_id: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("unit.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    material_cost: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    manufacturing_cost: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    overhead_cost: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    rule_version: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'v1'"))
    trace_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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

    part = relationship("Part")
    currency = relationship("Currency")
    unit = relationship("Unit")

    @property
    def part_code(self) -> Optional[str]:
        if self.part is None:
            return None
        return self.part.part_code

    @property
    def part_name(self) -> Optional[str]:
        if self.part is None:
            return None
        return self.part.part_name

    @property
    def currency_code(self) -> Optional[str]:
        if self.currency is None:
            return None
        return self.currency.currency_code

    @property
    def unit_code(self) -> Optional[str]:
        if self.unit is None:
            return None
        return self.unit.unit_code
