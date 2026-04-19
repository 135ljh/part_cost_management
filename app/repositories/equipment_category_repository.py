from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipment_category import EquipmentCategory


class EquipmentCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self) -> list[EquipmentCategory]:
        stmt = select(EquipmentCategory).order_by(
            EquipmentCategory.updated_at.desc(), EquipmentCategory.id.desc()
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, category_id: int) -> Optional[EquipmentCategory]:
        return self.db.get(EquipmentCategory, category_id)

    def create(self, category: EquipmentCategory) -> EquipmentCategory:
        self.db.add(category)
        self.db.flush()
        self.db.refresh(category)
        return category

    def delete(self, category: EquipmentCategory) -> None:
        self.db.delete(category)
        self.db.flush()

