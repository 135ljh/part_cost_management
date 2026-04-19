from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.region import Region
from app.repositories.region_repository import RegionRepository
from app.schemas.region import RegionCreate, RegionUpdate


class RegionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RegionRepository(db)

    def list_regions(self) -> list[Region]:
        return self.repo.list_regions()

    def get_region_detail(self, region_id: int) -> Region:
        region = self.repo.get_by_id(region_id)
        if not region:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="区域不存在")
        return region

    def _validate_parent(self, parent_id: int | None, current_id: int | None = None) -> None:
        if parent_id is None:
            return
        if current_id is not None and parent_id == current_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="上级区域不能是自身"
            )
        if not self.repo.get_by_id(parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="上级区域不存在"
            )

    def create_region(self, payload: RegionCreate) -> Region:
        self._validate_parent(payload.parent_id)
        region = Region(
            region_code=payload.region_code,
            region_name=payload.region_name,
            region_type=payload.region_type,
            parent_id=payload.parent_id,
            level_no=payload.level_no,
            full_name=payload.full_name,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(region)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：区域编码重复或约束冲突"
            )

    def update_region(self, region_id: int, payload: RegionUpdate) -> Region:
        region = self.get_region_detail(region_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        if "parent_id" in update_data:
            self._validate_parent(update_data["parent_id"], current_id=region_id)

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for field_name, value in update_data.items():
            setattr(region, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(region)
            return region
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：区域编码重复或约束冲突"
            )

    def delete_region(self, region_id: int) -> None:
        region = self.get_region_detail(region_id)
        self.repo.delete(region)
        self.db.commit()

