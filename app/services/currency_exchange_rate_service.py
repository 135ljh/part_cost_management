from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.currency import Currency
from app.models.currency_exchange_rate import CurrencyExchangeRate
from app.repositories.currency_exchange_rate_repository import (
    CurrencyExchangeRateRepository,
)
from app.schemas.currency_exchange_rate import (
    CurrencyExchangeRateCreate,
    CurrencyExchangeRateUpdate,
)


class CurrencyExchangeRateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CurrencyExchangeRateRepository(db)

    def list_rates(self) -> list[CurrencyExchangeRate]:
        return self.repo.list_rates()

    def get_rate_detail(self, rate_id: int) -> CurrencyExchangeRate:
        rate = self.repo.get_by_id(rate_id)
        if not rate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="汇率记录不存在")
        return rate

    def _validate_currency_pair(self, from_currency_id: int, to_currency_id: int) -> None:
        if from_currency_id == to_currency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="源货币和目标货币不能相同"
            )
        from_exists = self.db.get(Currency, from_currency_id)
        to_exists = self.db.get(Currency, to_currency_id)
        if not from_exists or not to_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="源货币或目标货币不存在"
            )

    def create_rate(self, payload: CurrencyExchangeRateCreate) -> CurrencyExchangeRate:
        self._validate_currency_pair(payload.from_currency_id, payload.to_currency_id)
        rate = CurrencyExchangeRate(
            from_currency_id=payload.from_currency_id,
            to_currency_id=payload.to_currency_id,
            rate_type=payload.rate_type,
            exchange_rate=payload.exchange_rate,
            effective_date=payload.effective_date,
            source_name=payload.source_name,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(rate)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="创建失败：汇率唯一约束冲突或外键冲突",
            )

    def update_rate(self, rate_id: int, payload: CurrencyExchangeRateUpdate) -> CurrencyExchangeRate:
        rate = self.get_rate_detail(rate_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        new_from = update_data.get("from_currency_id", rate.from_currency_id)
        new_to = update_data.get("to_currency_id", rate.to_currency_id)
        if "from_currency_id" in update_data or "to_currency_id" in update_data:
            self._validate_currency_pair(new_from, new_to)

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for field_name, value in update_data.items():
            setattr(rate, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(rate)
            return rate
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="更新失败：汇率唯一约束冲突或外键冲突",
            )

    def delete_rate(self, rate_id: int) -> None:
        rate = self.get_rate_detail(rate_id)
        self.repo.delete(rate)
        self.db.commit()

