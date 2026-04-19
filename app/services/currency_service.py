from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.currency import Currency
from app.repositories.currency_repository import CurrencyRepository
from app.schemas.currency import CurrencyCreate, CurrencyUpdate


class CurrencyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CurrencyRepository(db)

    def list_currencies(self) -> list[Currency]:
        return self.repo.list_currencies()

    def get_currency_detail(self, currency_id: int) -> Currency:
        currency = self.repo.get_by_id(currency_id)
        if not currency:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="货币不存在")
        return currency

    def create_currency(self, payload: CurrencyCreate) -> Currency:
        if payload.is_base_currency:
            existed_base = self.repo.get_base_currency()
            if existed_base:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="已存在基准货币"
                )

        currency = Currency(
            currency_code=payload.currency_code.upper(),
            currency_name=payload.currency_name,
            currency_symbol=payload.currency_symbol,
            precision_scale=payload.precision_scale,
            is_base_currency=1 if payload.is_base_currency else 0,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(currency)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="货币代码重复或数据冲突"
            )

    def update_currency(self, currency_id: int, payload: CurrencyUpdate) -> Currency:
        currency = self.get_currency_detail(currency_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        if "currency_code" in update_data and update_data["currency_code"] is not None:
            update_data["currency_code"] = update_data["currency_code"].upper()

        if "is_base_currency" in update_data and update_data["is_base_currency"]:
            existed_base = self.repo.get_base_currency()
            if existed_base and existed_base.id != currency_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="已存在其他基准货币"
                )

        if "is_base_currency" in update_data:
            update_data["is_base_currency"] = 1 if update_data["is_base_currency"] else 0
        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for field_name, value in update_data.items():
            setattr(currency, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(currency)
            return currency
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：货币代码重复或数据冲突"
            )

    def delete_currency(self, currency_id: int) -> None:
        currency = self.get_currency_detail(currency_id)
        try:
            self.repo.delete(currency)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联汇率或业务数据"
            )

