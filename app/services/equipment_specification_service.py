from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.equipment import Equipment
from app.models.equipment_specification import EquipmentSpecification
from app.models.unit import Unit
from app.repositories.equipment_specification_repository import EquipmentSpecificationRepository
from app.schemas.equipment_specification import (
    EquipmentSpecificationCreate,
    EquipmentSpecificationUpdate,
)


class EquipmentSpecificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EquipmentSpecificationRepository(db)

    def _validate_fk(self, equipment_id: int, spec_unit_id: int | None) -> None:
        if not self.db.get(Equipment, equipment_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="设备不存在")
        if spec_unit_id is not None and not self.db.get(Unit, spec_unit_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="规格单位不存在")

    def list_specs(self) -> list[EquipmentSpecification]:
        return self.repo.list_specs()

    def get_detail(self, spec_id: int) -> EquipmentSpecification:
        spec = self.repo.get_by_id(spec_id)
        if not spec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备规格不存在")
        return spec

    def create(self, payload: EquipmentSpecificationCreate) -> EquipmentSpecification:
        self._validate_fk(payload.equipment_id, payload.spec_unit_id)
        spec = EquipmentSpecification(
            equipment_id=payload.equipment_id,
            spec_key=payload.spec_key,
            spec_value=payload.spec_value,
            spec_unit_id=payload.spec_unit_id,
            sort_no=payload.sort_no,
        )
        try:
            created = self.repo.create(spec)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="创建冲突")

    def update(self, spec_id: int, payload: EquipmentSpecificationUpdate) -> EquipmentSpecification:
        spec = self.get_detail(spec_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        equipment_id = update_data.get("equipment_id", spec.equipment_id)
        spec_unit_id = update_data.get("spec_unit_id", spec.spec_unit_id)
        self._validate_fk(equipment_id, spec_unit_id)
        for k, v in update_data.items():
            setattr(spec, k, v)
        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(spec)
            return spec
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新冲突")

    def delete(self, spec_id: int) -> None:
        spec = self.get_detail(spec_id)
        self.repo.delete(spec)
        self.db.commit()

