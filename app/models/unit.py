from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Unit(Base):
    __tablename__ = "unit"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unit_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    unit_name: Mapped[str] = mapped_column(String(64), nullable=False)
    unit_display_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    unit_category: Mapped[str] = mapped_column(String(64), nullable=False)
    measurement_system: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    base_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("unit.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    unit_factor: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), nullable=False, server_default=text("1")
    )
    sync_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
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

