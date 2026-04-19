from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material import Material


class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_materials(self) -> list[Material]:
        stmt = select(Material).order_by(Material.updated_at.desc(), Material.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, material_id: int) -> Optional[Material]:
        return self.db.get(Material, material_id)

    def create(self, material: Material) -> Material:
        self.db.add(material)
        self.db.flush()
        self.db.refresh(material)
        return material

    def delete(self, material: Material) -> None:
        self.db.delete(material)
        self.db.flush()

