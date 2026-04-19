import random
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.material_category import MaterialCategory
from app.models.unit import Unit
from app.repositories.material_repository import MaterialRepository
from app.schemas.material import MaterialCreate, MaterialUpdate


class MaterialService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MaterialRepository(db)

    def list_materials(self) -> list[Material]:
        return self.repo.list_materials()

    def get_material_detail(self, material_id: int) -> Material:
        material = self.repo.get_by_id(material_id)
        if not material:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="物质不存在")
        return material

    def _generate_material_code(self) -> str:
        return f"MAT{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"

    def _validate_foreign_keys(
        self, category_id: int | None, density_unit_id: int | None
    ) -> None:
        if category_id is not None and not self.db.get(MaterialCategory, category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="物质类别不存在"
            )
        if density_unit_id is not None and not self.db.get(Unit, density_unit_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="密度单位不存在"
            )

    def create_material(self, payload: MaterialCreate) -> Material:
        self._validate_foreign_keys(payload.category_id, payload.density_unit_id)
        material = Material(
            material_code=payload.material_code or self._generate_material_code(),
            material_name=payload.material_name,
            category_id=payload.category_id,
            density=payload.density,
            density_unit_id=payload.density_unit_id,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(material)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：物质编码重复或约束冲突"
            )

    def update_material(self, material_id: int, payload: MaterialUpdate) -> Material:
        material = self.get_material_detail(material_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        new_category_id = update_data.get("category_id", material.category_id)
        new_density_unit_id = update_data.get("density_unit_id", material.density_unit_id)
        self._validate_foreign_keys(new_category_id, new_density_unit_id)

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for field_name, value in update_data.items():
            setattr(material, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(material)
            return material
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突"
            )

    def delete_material(self, material_id: int) -> None:
        material = self.get_material_detail(material_id)
        try:
            self.repo.delete(material)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据"
            )

