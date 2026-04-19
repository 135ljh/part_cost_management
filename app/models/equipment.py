from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    equipment_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    equipment_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("equipment_category.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    equipment_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    energy_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    specification_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scale_desc: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
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

