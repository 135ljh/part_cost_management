from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.equipment_category import (
    EquipmentCategoryCreate,
    EquipmentCategoryRead,
    EquipmentCategoryUpdate,
)
from app.services.equipment_category_service import EquipmentCategoryService


router = APIRouter(prefix="/equipment-categories", tags=["设备分类配置"])


@router.get("", response_model=list[EquipmentCategoryRead], summary="设备分类列表")
def list_equipment_categories(db: Session = Depends(get_db)) -> list[EquipmentCategoryRead]:
    return EquipmentCategoryService(db).list_categories()


@router.get("/{category_id}", response_model=EquipmentCategoryRead, summary="设备分类详情")
def get_equipment_category(category_id: int, db: Session = Depends(get_db)) -> EquipmentCategoryRead:
    return EquipmentCategoryService(db).get_detail(category_id)


@router.post("", response_model=EquipmentCategoryRead, status_code=status.HTTP_201_CREATED, summary="新建设备分类")
def create_equipment_category(
    payload: EquipmentCategoryCreate, db: Session = Depends(get_db)
) -> EquipmentCategoryRead:
    return EquipmentCategoryService(db).create(payload)


@router.put("/{category_id}", response_model=EquipmentCategoryRead, summary="更新设备分类")
def update_equipment_category(
    category_id: int, payload: EquipmentCategoryUpdate, db: Session = Depends(get_db)
) -> EquipmentCategoryRead:
    return EquipmentCategoryService(db).update(category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除设备分类")
def delete_equipment_category(category_id: int, db: Session = Depends(get_db)) -> Response:
    EquipmentCategoryService(db).delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

