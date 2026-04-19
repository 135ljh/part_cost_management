from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.unit import Unit
from app.repositories.unit_repository import UnitRepository
from app.schemas.unit import UnitCreate, UnitUpdate


class UnitService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UnitRepository(db)

    def list_units(self) -> list[Unit]:
        return self.repo.list_units()

    def get_unit_detail(self, unit_id: int) -> Unit:
        unit = self.repo.get_by_id(unit_id)
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="单位不存在")
        return unit

    def create_unit(self, payload: UnitCreate) -> Unit:
        if payload.base_unit_id is not None and not self.repo.get_by_id(payload.base_unit_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="基准单位不存在"
            )

        unit = Unit(
            unit_code=payload.unit_code,
            unit_name=payload.unit_name,
            unit_display_name=payload.unit_display_name,
            unit_category=payload.unit_category,
            measurement_system=payload.measurement_system,
            base_unit_id=payload.base_unit_id,
            unit_factor=payload.unit_factor,
            sync_time=payload.sync_time,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )

        try:
            created = self.repo.create(unit)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="单位编码重复或数据约束冲突"
            )

    def update_unit(self, unit_id: int, payload: UnitUpdate) -> Unit:
        unit = self.get_unit_detail(unit_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        if "base_unit_id" in update_data:
            base_unit_id = update_data["base_unit_id"]
            if base_unit_id == unit_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="基准单位不能是自身"
                )
            if base_unit_id is not None and not self.repo.get_by_id(base_unit_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="基准单位不存在"
                )

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for field_name, value in update_data.items():
            setattr(unit, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(unit)
            return unit
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：单位编码重复或数据冲突"
            )

    def delete_unit(self, unit_id: int) -> None:
        unit = self.get_unit_detail(unit_id)
        try:
            self.repo.delete(unit)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据约束"
            )

