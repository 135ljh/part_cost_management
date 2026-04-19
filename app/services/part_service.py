from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.material_category import MaterialCategory
from app.models.material_type import MaterialType
from app.models.part import Part
from app.models.unit import Unit
from app.repositories.part_repository import PartRepository
from app.schemas.part import PartCreate, PartUpdate


class PartService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PartRepository(db)

    def list_parts(self) -> list[Part]:
        return self.repo.list_parts()

    def get_part_detail(self, part_id: int) -> Part:
        part = self.repo.get_by_id(part_id)
        if not part:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="零件不存在")
        return part

    def _validate_foreign_keys(
        self,
        material_type_id: int | None,
        material_category_id: int | None,
        preferred_material_id: int | None,
        quantity_unit_id: int | None,
    ) -> None:
        if material_type_id is not None and not self.db.get(MaterialType, material_type_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="所属物料类型不存在"
            )
        if material_category_id is not None and not self.db.get(MaterialCategory, material_category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="所属物料分类不存在"
            )
        if preferred_material_id is not None and not self.db.get(Material, preferred_material_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="默认物料不存在"
            )
        if quantity_unit_id is not None and not self.db.get(Unit, quantity_unit_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="数量单位不存在"
            )

    def create_part(self, payload: PartCreate) -> Part:
        self._validate_foreign_keys(
            payload.material_type_id,
            payload.material_category_id,
            payload.preferred_material_id,
            payload.quantity_unit_id,
        )
        existed = self.repo.get_by_code(payload.part_code)
        if existed is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：零件编码已存在"
            )
        part = Part(
            part_code=payload.part_code,
            part_name=payload.part_name,
            part_description=payload.part_description,
            part_type=payload.part_type,
            material_category_id=payload.material_category_id,
            material_type_id=payload.material_type_id,
            preferred_material_id=payload.preferred_material_id,
            quantity_unit_id=payload.quantity_unit_id,
            surface_area=payload.surface_area,
            volume=payload.volume,
            cad_file_url=payload.cad_file_url,
            target_url=payload.target_url,
            legacy_result=payload.legacy_result,
            legacy_msg=payload.legacy_msg,
            part_status=payload.part_status,
            lifecycle_stage=payload.lifecycle_stage,
            revision_no=payload.revision_no,
            version_no=payload.version_no,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(part)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：零件编码重复或约束冲突"
            )

    def update_part(self, part_id: int, payload: PartUpdate) -> Part:
        part = self.get_part_detail(part_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        new_material_type_id = update_data.get("material_type_id", part.material_type_id)
        new_material_category_id = update_data.get("material_category_id", part.material_category_id)
        new_preferred_material_id = update_data.get("preferred_material_id", part.preferred_material_id)
        new_quantity_unit_id = update_data.get("quantity_unit_id", part.quantity_unit_id)
        self._validate_foreign_keys(
            new_material_type_id,
            new_material_category_id,
            new_preferred_material_id,
            new_quantity_unit_id,
        )
        if "part_code" in update_data:
            existed = self.repo.get_by_code(update_data["part_code"])
            if existed is not None and existed.id != part.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="更新失败：零件编码已存在"
                )

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for field_name, value in update_data.items():
            setattr(part, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            refreshed = self.repo.get_by_id(part.id)
            if refreshed is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="零件不存在")
            return refreshed
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突"
            )

    def delete_part(self, part_id: int) -> None:
        part = self.get_part_detail(part_id)
        try:
            self.repo.delete(part)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据"
            )
