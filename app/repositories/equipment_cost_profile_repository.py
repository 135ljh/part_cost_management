from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipment_cost_profile import EquipmentCostProfile


class EquipmentCostProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_profiles(self) -> list[EquipmentCostProfile]:
        stmt = select(EquipmentCostProfile).order_by(
            EquipmentCostProfile.updated_at.desc(), EquipmentCostProfile.id.desc()
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, profile_id: int) -> Optional[EquipmentCostProfile]:
        return self.db.get(EquipmentCostProfile, profile_id)

    def create(self, profile: EquipmentCostProfile) -> EquipmentCostProfile:
        self.db.add(profile)
        self.db.flush()
        self.db.refresh(profile)
        return profile

    def delete(self, profile: EquipmentCostProfile) -> None:
        self.db.delete(profile)
        self.db.flush()

