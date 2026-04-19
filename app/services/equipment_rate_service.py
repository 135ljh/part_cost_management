import random
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.currency import Currency
from app.models.equipment import Equipment
from app.models.equipment_category import EquipmentCategory
from app.models.equipment_rate import EquipmentRate
from app.repositories.equipment_rate_repository import EquipmentRateRepository
from app.schemas.equipment_rate import EquipmentRateCreate, EquipmentRateRead, EquipmentRateUpdate


class EquipmentRateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EquipmentRateRepository(db)

    def _generate_code(self) -> str:
        return f"ER{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def _resolve_equipment(
        self, equipment_id: int | None, equipment_number: str | None
    ) -> int | None:
        if equipment_id:
            if not self.db.get(Equipment, equipment_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="设备不存在")
            return equipment_id
        if equipment_number:
            stmt = select(Equipment).where(Equipment.equipment_code == equipment_number)
            equipment = self.db.scalar(stmt)
            if not equipment:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="设备编号不存在")
            return equipment.id
        return None

    def _resolve_equipment_category(
        self, category_id: int | None, category_name: str | None
    ) -> int | None:
        if category_id:
            if not self.db.get(EquipmentCategory, category_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="设备类别不存在"
                )
            return category_id
        if category_name:
            stmt = select(EquipmentCategory).where(EquipmentCategory.category_name == category_name)
            category = self.db.scalar(stmt)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="设备类别名称不存在"
                )
            return category.id
        return None

    def _validate_currency(self, currency_id: int | None) -> None:
        if currency_id and not self.db.get(Currency, currency_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="币种不存在")

    def _to_read(self, rate: EquipmentRate) -> EquipmentRateRead:
        base = EquipmentRateRead.model_validate(rate)
        equipment_number = None
        category_name = None
        if rate.equipment_id:
            e = self.db.get(Equipment, rate.equipment_id)
            equipment_number = e.equipment_code if e else None
        if rate.equipment_category_id:
            c = self.db.get(EquipmentCategory, rate.equipment_category_id)
            category_name = c.category_name if c else None
        return base.model_copy(
            update={
                "equipment_number": equipment_number,
                "equipment_category_name": category_name,
            }
        )

    def list_rates(self) -> list[EquipmentRateRead]:
        return [self._to_read(x) for x in self.repo.list_rates()]

    def get_rate_detail(self, rate_id: int) -> EquipmentRateRead:
        rate = self.repo.get_by_id(rate_id)
        if not rate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备费率不存在")
        return self._to_read(rate)

    def create_rate(self, payload: EquipmentRateCreate) -> EquipmentRateRead:
        equipment_id = self._resolve_equipment(payload.equipment_id, payload.equipment_number)
        category_id = self._resolve_equipment_category(
            payload.equipment_category_id, payload.equipment_category_name
        )
        self._validate_currency(payload.currency_id)

        rate = EquipmentRate(
            rate_code=payload.rate_code or self._generate_code(),
            equipment_id=equipment_id,
            equipment_category_id=category_id,
            description=payload.description,
            equipment_type=payload.equipment_type,
            manpower=payload.manpower,
            labor_group=payload.labor_group,
            direct_labor=payload.direct_labor,
            direct_fringe=payload.direct_fringe,
            indirect_labor=payload.indirect_labor,
            indirect_fringe=payload.indirect_fringe,
            total_labor=payload.total_labor,
            depreciation=payload.depreciation,
            insurance=payload.insurance,
            floor_space=payload.floor_space,
            mro_labor=payload.mro_labor,
            utilities=payload.utilities,
            indirect_materials=payload.indirect_materials,
            other_burden=payload.other_burden,
            total_burden=payload.total_burden,
            total_minute_rate=payload.total_minute_rate,
            investment=payload.investment,
            currency_id=payload.currency_id,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(rate)
            self.db.commit()
            return self._to_read(created)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：费率编码重复或约束冲突"
            )

    def update_rate(self, rate_id: int, payload: EquipmentRateUpdate) -> EquipmentRateRead:
        rate = self.repo.get_by_id(rate_id)
        if not rate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备费率不存在")

        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        if "equipment_id" in update_data or "equipment_number" in update_data:
            equipment_id = self._resolve_equipment(
                update_data.get("equipment_id"), update_data.get("equipment_number")
            )
            update_data["equipment_id"] = equipment_id
        if "equipment_category_id" in update_data or "equipment_category_name" in update_data:
            category_id = self._resolve_equipment_category(
                update_data.get("equipment_category_id"),
                update_data.get("equipment_category_name"),
            )
            update_data["equipment_category_id"] = category_id
        if "currency_id" in update_data:
            self._validate_currency(update_data["currency_id"])

        update_data.pop("equipment_number", None)
        update_data.pop("equipment_category_name", None)

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for k, v in update_data.items():
            setattr(rate, k, v)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(rate)
            return self._to_read(rate)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突"
            )

    def delete_rate(self, rate_id: int) -> None:
        rate = self.repo.get_by_id(rate_id)
        if not rate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备费率不存在")
        self.repo.delete(rate)
        self.db.commit()

