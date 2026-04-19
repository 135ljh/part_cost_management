from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.material_category import MaterialCategory


class MaterialCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self) -> list[MaterialCategory]:
        stmt = select(MaterialCategory).order_by(
            MaterialCategory.updated_at.desc(), MaterialCategory.id.desc()
        )
        return list(self.db.scalars(stmt).all())

    def list_all_for_tree(self) -> list[MaterialCategory]:
        stmt = select(MaterialCategory).order_by(MaterialCategory.id.asc())
        return list(self.db.scalars(stmt).all())

    def list_material_briefs(self) -> list[tuple[int, int, str]]:
        stmt = select(Material.id, Material.category_id, Material.material_name).where(
            Material.category_id.is_not(None)
        )
        return list(self.db.execute(stmt).all())

    def get_by_id(self, category_id: int) -> Optional[MaterialCategory]:
        return self.db.get(MaterialCategory, category_id)

    def create(self, category: MaterialCategory) -> MaterialCategory:
        self.db.add(category)
        self.db.flush()
        self.db.refresh(category)
        return category

    def delete(self, category: MaterialCategory) -> None:
        self.db.delete(category)
        self.db.flush()

