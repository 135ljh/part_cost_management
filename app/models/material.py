from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Material(Base):
    __tablename__ = "material"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    material_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material_category.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    density: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8), nullable=True)
    density_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("unit.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    default_quantity_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("unit.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    scrap_material_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )
    specification: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
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

