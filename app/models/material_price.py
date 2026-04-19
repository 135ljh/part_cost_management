from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MaterialPrice(Base):
    __tablename__ = "material_price"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_id: Mapped[int] = mapped_column(
        ForeignKey("material.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("region.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    supplier_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    price_unit_id: Mapped[int] = mapped_column(
        ForeignKey("unit.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
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

