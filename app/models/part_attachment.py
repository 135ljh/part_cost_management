from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PartAttachment(Base):
    __tablename__ = "part_attachment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    part_id: Mapped[int] = mapped_column(
        ForeignKey("part.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    source_type: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("'UPLOAD'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    part = relationship("Part")

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

