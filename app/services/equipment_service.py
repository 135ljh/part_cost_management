from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.models.equipment_category import EquipmentCategory
from app.repositories.equipment_repository import EquipmentRepository
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


class EquipmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EquipmentRepository(db)

    def _validate_category(self, category_id: int | None) -> None:
        if category_id is not None and not self.db.get(EquipmentCategory, category_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="设备分类不存在")

    def list_equipment(self) -> list[Equipment]:
        return self.repo.list_equipment()

    def get_detail(self, equipment_id: int) -> Equipment:
        equipment = self.repo.get_by_id(equipment_id)
        if not equipment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备不存在")
        return equipment

    def create(self, payload: EquipmentCreate) -> Equipment:
        self._validate_category(payload.category_id)
        equipment = Equipment(
            equipment_code=payload.equipment_code,
            equipment_name=payload.equipment_name,
            category_id=payload.category_id,
            equipment_type=payload.equipment_type,
            manufacturer=payload.manufacturer,
            energy_type=payload.energy_type,
            specification_text=payload.specification_text,
            scale_desc=payload.scale_desc,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(equipment)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="设备编号重复或数据冲突")

    def update(self, equipment_id: int, payload: EquipmentUpdate) -> Equipment:
        equipment = self.get_detail(equipment_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        if "category_id" in update_data:
            self._validate_category(update_data["category_id"])
        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0
        for k, v in update_data.items():
            setattr(equipment, k, v)
        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(equipment)
            return equipment
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新冲突")

    def delete(self, equipment_id: int) -> None:
        equipment = self.get_detail(equipment_id)
        try:
            self.repo.delete(equipment)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="存在关联数据，无法删除")

