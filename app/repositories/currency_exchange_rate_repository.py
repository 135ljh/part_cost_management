from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.currency_exchange_rate import CurrencyExchangeRate


class CurrencyExchangeRateRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_rates(self) -> list[CurrencyExchangeRate]:
        stmt = select(CurrencyExchangeRate).order_by(
            CurrencyExchangeRate.effective_date.desc(), CurrencyExchangeRate.id.desc()
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, rate_id: int) -> Optional[CurrencyExchangeRate]:
        return self.db.get(CurrencyExchangeRate, rate_id)

    def create(self, rate: CurrencyExchangeRate) -> CurrencyExchangeRate:
        self.db.add(rate)
        self.db.flush()
        self.db.refresh(rate)
        return rate

    def delete(self, rate: CurrencyExchangeRate) -> None:
        self.db.delete(rate)
        self.db.flush()

