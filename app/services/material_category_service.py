import random
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.material_category import MaterialCategory
from app.repositories.material_category_repository import MaterialCategoryRepository
from app.schemas.material_category import (
    MaterialCategoryCreate,
    MaterialCategoryTreeNode,
    MaterialCategoryUpdate,
    MaterialInCategoryNode,
)


class MaterialCategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MaterialCategoryRepository(db)

    def list_categories(self) -> list[MaterialCategory]:
        return self.repo.list_categories()

    def get_category_detail(self, category_id: int) -> MaterialCategory:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="物质分类不存在")
        return category

    def _generate_category_code(self) -> str:
        return f"MCAT{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"

    def _validate_parent(self, parent_id: int | None, current_id: int | None = None) -> None:
        if parent_id is None:
            return
        if current_id is not None and parent_id == current_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="父物质分类不能是自身"
            )
        if not self.repo.get_by_id(parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="父物质分类不存在"
            )
        if current_id is not None and self._is_descendant(current_id, parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="父物质分类不能设置为当前分类的子分类"
            )

    def _is_descendant(self, current_id: int, candidate_parent_id: int) -> bool:
        all_categories = self.repo.list_all_for_tree()
        parent_map = {c.id: c.parent_id for c in all_categories}
        cursor = candidate_parent_id
        visited: set[int] = set()
        while cursor is not None and cursor not in visited:
            if cursor == current_id:
                return True
            visited.add(cursor)
            cursor = parent_map.get(cursor)
        return False

    def create_category(self, payload: MaterialCategoryCreate) -> MaterialCategory:
        self._validate_parent(payload.parent_id)
        category = MaterialCategory(
            category_code=payload.category_code or self._generate_category_code(),
            category_name=payload.category_name,
            category_type=payload.category_type,
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：分类编码重复或约束冲突"
            )

    def update_category(
        self, category_id: int, payload: MaterialCategoryUpdate
    ) -> MaterialCategory:
        category = self.get_category_detail(category_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        if "parent_id" in update_data:
            self._validate_parent(update_data["parent_id"], current_id=category_id)

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for field_name, value in update_data.items():
            setattr(category, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(category)
            return category
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：分类编码重复或约束冲突"
            )

    def delete_category(self, category_id: int) -> None:
        category = self.get_category_detail(category_id)
        try:
            self.repo.delete(category)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在子分类或关联物质"
            )

    def get_category_tree(self) -> list[MaterialCategoryTreeNode]:
        categories = self.repo.list_all_for_tree()
        material_rows = self.repo.list_material_briefs()

        node_map: dict[int, MaterialCategoryTreeNode] = {}
        for c in categories:
            node_map[c.id] = MaterialCategoryTreeNode(
                id=c.id,
                category_name=c.category_name,
                parent_id=c.parent_id,
                materials=[],
                children=[],
            )

        for m_id, category_id, material_name in material_rows:
            if category_id in node_map:
                node_map[category_id].materials.append(
                    MaterialInCategoryNode(id=m_id, material_name=material_name)
                )

        roots: list[MaterialCategoryTreeNode] = []
        for c in categories:
            current = node_map[c.id]
            if c.parent_id and c.parent_id in node_map:
                node_map[c.parent_id].children.append(current)
            else:
                roots.append(current)
        return roots

