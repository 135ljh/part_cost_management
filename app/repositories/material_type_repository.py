from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material_type import MaterialType


class MaterialTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_material_types(self) -> list[MaterialType]:
        stmt = select(MaterialType).order_by(MaterialType.updated_at.desc(), MaterialType.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, material_type_id: int) -> Optional[MaterialType]:
        return self.db.get(MaterialType, material_type_id)

    def create(self, material_type: MaterialType) -> MaterialType:
        self.db.add(material_type)
        self.db.flush()
        self.db.refresh(material_type)
        return material_type

    def delete(self, material_type: MaterialType) -> None:
        self.db.delete(material_type)
        self.db.flush()
