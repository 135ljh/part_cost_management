from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.currency import Currency
from app.models.equipment import Equipment
from app.models.equipment_cost_profile import EquipmentCostProfile
from app.repositories.equipment_cost_profile_repository import EquipmentCostProfileRepository
from app.schemas.equipment_cost_profile import (
    EquipmentCostProfileCreate,
    EquipmentCostProfileUpdate,
)


class EquipmentCostProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EquipmentCostProfileRepository(db)

    def _validate_fk(self, equipment_id: int, currency_id: int) -> None:
        if not self.db.get(Equipment, equipment_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="设备不存在")
        if not self.db.get(Currency, currency_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="币种不存在")

    def list_profiles(self) -> list[EquipmentCostProfile]:
        return self.repo.list_profiles()

    def get_detail(self, profile_id: int) -> EquipmentCostProfile:
        profile = self.repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备成本配置不存在")
        return profile

    def create(self, payload: EquipmentCostProfileCreate) -> EquipmentCostProfile:
        self._validate_fk(payload.equipment_id, payload.currency_id)
        data = payload.model_dump()
        data["is_active"] = 1 if payload.is_active else 0
        profile = EquipmentCostProfile(**data)
        try:
            created = self.repo.create(profile)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="创建冲突")

    def update(self, profile_id: int, payload: EquipmentCostProfileUpdate) -> EquipmentCostProfile:
        profile = self.get_detail(profile_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        equipment_id = update_data.get("equipment_id", profile.equipment_id)
        currency_id = update_data.get("currency_id", profile.currency_id)
        self._validate_fk(equipment_id, currency_id)
        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0
        for k, v in update_data.items():
            setattr(profile, k, v)
        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新冲突")

    def delete(self, profile_id: int) -> None:
        profile = self.get_detail(profile_id)
        self.repo.delete(profile)
        self.db.commit()
