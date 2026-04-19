from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Part(Base):
    __tablename__ = "part"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    part_code: Mapped[str] = mapped_column("part_number", String(64), nullable=False)
    part_name: Mapped[str] = mapped_column(String(128), nullable=False)
    part_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    part_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    material_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material_category.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    material_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material_type.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    preferred_material_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("material.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    quantity_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("unit.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    surface_area: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8), nullable=True)
    volume: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8), nullable=True)
    cad_file_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    legacy_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    legacy_msg: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    part_status: Mapped[str] = mapped_column(
        "lifecycle_status", String(64), nullable=False, server_default=text("'DRAFT'")
    )
    lifecycle_stage: Mapped[Optional[str]] = mapped_column("process_type", String(64), nullable=True)
    revision_no: Mapped[Optional[str]] = mapped_column("part_version", String(64), nullable=True)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
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

    material_type = relationship("MaterialType")
    material_category = relationship("MaterialCategory")
    preferred_material = relationship("Material")
    quantity_unit = relationship("Unit")

    @property
    def material_type_name(self) -> Optional[str]:
        if self.material_type is None:
            return None
        return self.material_type.material_type_name

    @property
    def material_category_name(self) -> Optional[str]:
        if self.material_category is None:
            return None
        return self.material_category.category_name

    @property
    def preferred_material_name(self) -> Optional[str]:
        if self.preferred_material is None:
            return None
        return self.preferred_material.material_name

    @property
    def quantity_unit_name(self) -> Optional[str]:
        if self.quantity_unit is None:
            return None
        return self.quantity_unit.unit_name
