from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.material_type import MaterialType
from app.repositories.material_type_repository import MaterialTypeRepository
from app.schemas.material_type import MaterialTypeCreate, MaterialTypeUpdate


class MaterialTypeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MaterialTypeRepository(db)

    def list_material_types(self) -> list[MaterialType]:
        return self.repo.list_material_types()

    def get_material_type_detail(self, material_type_id: int) -> MaterialType:
        material_type = self.repo.get_by_id(material_type_id)
        if not material_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="物料类型不存在"
            )
        return material_type

    def create_material_type(self, payload: MaterialTypeCreate) -> MaterialType:
        material_type = MaterialType(
            material_type_code=payload.material_type_code,
            material_type_name=payload.material_type_name,
            description=payload.description,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(material_type)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：物料类型编码重复或约束冲突"
            )

    def update_material_type(
        self, material_type_id: int, payload: MaterialTypeUpdate
    ) -> MaterialType:
        material_type = self.get_material_type_detail(material_type_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0
        for field_name, value in update_data.items():
            setattr(material_type, field_name, value)
        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(material_type)
            return material_type
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突"
            )

    def delete_material_type(self, material_type_id: int) -> None:
        material_type = self.get_material_type_detail(material_type_id)
        try:
            self.repo.delete(material_type)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据"
            )
