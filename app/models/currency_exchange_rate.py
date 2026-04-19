from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CurrencyExchangeRate(Base):
    __tablename__ = "currency_exchange_rate"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    to_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False
    )
    rate_type: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
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

