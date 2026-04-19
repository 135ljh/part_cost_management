from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipment_rate import EquipmentRate


class EquipmentRateRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_rates(self) -> list[EquipmentRate]:
        stmt = select(EquipmentRate).order_by(
            EquipmentRate.updated_at.desc(), EquipmentRate.id.desc()
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, rate_id: int) -> Optional[EquipmentRate]:
        return self.db.get(EquipmentRate, rate_id)

    def create(self, rate: EquipmentRate) -> EquipmentRate:
        self.db.add(rate)
        self.db.flush()
        self.db.refresh(rate)
        return rate

    def delete(self, rate: EquipmentRate) -> None:
        self.db.delete(rate)
        self.db.flush()

