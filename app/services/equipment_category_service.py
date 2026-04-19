import random
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.equipment_category import EquipmentCategory
from app.repositories.equipment_category_repository import EquipmentCategoryRepository
from app.schemas.equipment_category import EquipmentCategoryCreate, EquipmentCategoryUpdate


class EquipmentCategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EquipmentCategoryRepository(db)

    def _gen_code(self) -> str:
        return f"EQC{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def _validate_parent(self, parent_id: int | None, current_id: int | None = None) -> None:
        if parent_id is None:
            return
        if current_id is not None and parent_id == current_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="父分类不能是自身")
        if not self.repo.get_by_id(parent_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="父分类不存在")

    def list_categories(self) -> list[EquipmentCategory]:
        return self.repo.list_categories()

    def get_detail(self, category_id: int) -> EquipmentCategory:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备分类不存在")
        return category

    def create(self, payload: EquipmentCategoryCreate) -> EquipmentCategory:
        self._validate_parent(payload.parent_id)
        category = EquipmentCategory(
            category_code=payload.category_code or self._gen_code(),
            category_name=payload.category_name,
            parent_id=payload.parent_id,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(category)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="编码重复或数据冲突")

    def update(self, category_id: int, payload: EquipmentCategoryUpdate) -> EquipmentCategory:
        category = self.get_detail(category_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        if "parent_id" in update_data:
            self._validate_parent(update_data["parent_id"], current_id=category_id)
        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0
        for k, v in update_data.items():
            setattr(category, k, v)
        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(category)
            return category
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新冲突")

    def delete(self, category_id: int) -> None:
        category = self.get_detail(category_id)
        try:
            self.repo.delete(category)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="存在关联设备，无法删除")

