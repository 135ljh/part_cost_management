from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.unit import Unit


class UnitRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_units(self) -> list[Unit]:
        stmt = select(Unit).order_by(Unit.updated_at.desc(), Unit.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, unit_id: int) -> Optional[Unit]:
        return self.db.get(Unit, unit_id)

    def get_by_code(self, unit_code: str) -> Optional[Unit]:
        stmt = select(Unit).where(Unit.unit_code == unit_code)
        return self.db.scalar(stmt)

    def create(self, unit: Unit) -> Unit:
        self.db.add(unit)
        self.db.flush()
        self.db.refresh(unit)
        return unit

    def delete(self, unit: Unit) -> None:
        self.db.delete(unit)
        self.db.flush()

