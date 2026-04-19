from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.part import Part


class PartRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_parts(self) -> list[Part]:
        stmt = (
            select(Part)
            .options(
                selectinload(Part.material_type),
                selectinload(Part.material_category),
                selectinload(Part.preferred_material),
                selectinload(Part.quantity_unit),
            )
            .order_by(Part.updated_at.desc(), Part.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, part_id: int) -> Optional[Part]:
        stmt = (
            select(Part)
            .options(
                selectinload(Part.material_type),
                selectinload(Part.material_category),
                selectinload(Part.preferred_material),
                selectinload(Part.quantity_unit),
            )
            .where(Part.id == part_id)
        )
        return self.db.scalars(stmt).first()

    def get_by_code(self, part_code: str) -> Optional[Part]:
        stmt = (
            select(Part)
            .options(
                selectinload(Part.material_type),
                selectinload(Part.material_category),
                selectinload(Part.preferred_material),
                selectinload(Part.quantity_unit),
            )
            .where(Part.part_code == part_code)
        )
        return self.db.scalars(stmt).first()

    def create(self, part: Part) -> Part:
        self.db.add(part)
        self.db.flush()
        self.db.refresh(part)
        return part

    def delete(self, part: Part) -> None:
        self.db.delete(part)
        self.db.flush()
