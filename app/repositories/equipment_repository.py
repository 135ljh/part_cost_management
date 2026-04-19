from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipment import Equipment


class EquipmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_equipment(self) -> list[Equipment]:
        stmt = select(Equipment).order_by(Equipment.updated_at.desc(), Equipment.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, equipment_id: int) -> Optional[Equipment]:
        return self.db.get(Equipment, equipment_id)

    def get_by_code(self, equipment_code: str) -> Optional[Equipment]:
        stmt = select(Equipment).where(Equipment.equipment_code == equipment_code)
        return self.db.scalar(stmt)

    def create(self, equipment: Equipment) -> Equipment:
        self.db.add(equipment)
        self.db.flush()
        self.db.refresh(equipment)
        return equipment

    def delete(self, equipment: Equipment) -> None:
        self.db.delete(equipment)
        self.db.flush()

