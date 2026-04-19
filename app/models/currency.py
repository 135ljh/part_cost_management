from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Currency(Base):
    __tablename__ = "currency"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    currency_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    currency_name: Mapped[str] = mapped_column(String(64), nullable=False)
    currency_symbol: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    precision_scale: Mapped[int] = mapped_column(nullable=False, server_default=text("2"))
    is_base_currency: Mapped[int] = mapped_column(
        nullable=False, server_default=text("0")
    )
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

