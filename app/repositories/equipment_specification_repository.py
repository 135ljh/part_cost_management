from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipment_specification import EquipmentSpecification


class EquipmentSpecificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_specs(self) -> list[EquipmentSpecification]:
        stmt = select(EquipmentSpecification).order_by(
            EquipmentSpecification.equipment_id.asc(),
            EquipmentSpecification.sort_no.asc(),
            EquipmentSpecification.id.asc(),
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, spec_id: int) -> Optional[EquipmentSpecification]:
        return self.db.get(EquipmentSpecification, spec_id)

    def create(self, spec: EquipmentSpecification) -> EquipmentSpecification:
        self.db.add(spec)
        self.db.flush()
        self.db.refresh(spec)
        return spec

    def delete(self, spec: EquipmentSpecification) -> None:
        self.db.delete(spec)
        self.db.flush()

