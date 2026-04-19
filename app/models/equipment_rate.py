from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EquipmentRate(Base):
    __tablename__ = "equipment_rate"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rate_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    equipment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("equipment.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    equipment_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("equipment_category.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    equipment_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    manpower: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    labor_group: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    direct_labor: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    direct_fringe: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    indirect_labor: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    indirect_fringe: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    total_labor: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    depreciation: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    insurance: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    floor_space: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    mro_labor: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    utilities: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    indirect_materials: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    other_burden: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    total_burden: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    total_minute_rate: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    investment: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("0")
    )
    currency_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("currency.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
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

