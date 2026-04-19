from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.currency import Currency


class CurrencyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_currencies(self) -> list[Currency]:
        stmt = select(Currency).order_by(Currency.updated_at.desc(), Currency.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, currency_id: int) -> Optional[Currency]:
        return self.db.get(Currency, currency_id)

    def get_by_code(self, currency_code: str) -> Optional[Currency]:
        stmt = select(Currency).where(Currency.currency_code == currency_code)
        return self.db.scalar(stmt)

    def get_base_currency(self) -> Optional[Currency]:
        stmt = select(Currency).where(Currency.is_base_currency == 1).limit(1)
        return self.db.scalar(stmt)

    def create(self, currency: Currency) -> Currency:
        self.db.add(currency)
        self.db.flush()
        self.db.refresh(currency)
        return currency

    def delete(self, currency: Currency) -> None:
        self.db.delete(currency)
        self.db.flush()

