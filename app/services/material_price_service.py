from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.currency import Currency
from app.models.material import Material
from app.models.material_price import MaterialPrice
from app.models.region import Region
from app.models.unit import Unit
from app.repositories.material_price_repository import MaterialPriceRepository
from app.schemas.material_price import MaterialPriceCreate, MaterialPriceUpdate


class MaterialPriceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MaterialPriceRepository(db)

    def _validate_fk(
        self, material_id: int, currency_id: int, price_unit_id: int, region_id: int | None
    ) -> None:
        if not self.db.get(Material, material_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="物质不存在")
        if not self.db.get(Currency, currency_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="币种不存在")
        if not self.db.get(Unit, price_unit_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="价格单位不存在")
        if region_id is not None and not self.db.get(Region, region_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="区域不存在")

    def list_prices(self) -> list[MaterialPrice]:
        return self.repo.list_prices()

    def get_detail(self, price_id: int) -> MaterialPrice:
        price = self.repo.get_by_id(price_id)
        if not price:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="物质价格不存在")
        return price

    def create(self, payload: MaterialPriceCreate) -> MaterialPrice:
        self._validate_fk(payload.material_id, payload.currency_id, payload.price_unit_id, payload.region_id)
        price = MaterialPrice(
            material_id=payload.material_id,
            region_id=payload.region_id,
            supplier_name=payload.supplier_name,
            currency_id=payload.currency_id,
            price_unit_id=payload.price_unit_id,
            unit_price=payload.unit_price,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            source_name=payload.source_name,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(price)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="创建冲突")

    def update(self, price_id: int, payload: MaterialPriceUpdate) -> MaterialPrice:
        price = self.get_detail(price_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        material_id = update_data.get("material_id", price.material_id)
        currency_id = update_data.get("currency_id", price.currency_id)
        price_unit_id = update_data.get("price_unit_id", price.price_unit_id)
        region_id = update_data.get("region_id", price.region_id)
        self._validate_fk(material_id, currency_id, price_unit_id, region_id)
        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0
        for k, v in update_data.items():
            setattr(price, k, v)
        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(price)
            return price
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新冲突")

    def delete(self, price_id: int) -> None:
        price = self.get_detail(price_id)
        self.repo.delete(price)
        self.db.commit()

