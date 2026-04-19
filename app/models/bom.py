from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Bom(Base):
    __tablename__ = "bom"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    part_id: Mapped[int] = mapped_column(
        ForeignKey("part.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    bom_code: Mapped[str] = mapped_column(String(64), nullable=False)
    bom_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    version_no: Mapped[str] = mapped_column(String(64), nullable=False, server_default=text("'V1'"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'DRAFT'"))
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
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
    items = relationship("BomItem", back_populates="bom", cascade="all, delete-orphan")

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

