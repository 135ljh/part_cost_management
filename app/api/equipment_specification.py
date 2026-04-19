from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.equipment_specification import (
    EquipmentSpecificationCreate,
    EquipmentSpecificationRead,
    EquipmentSpecificationUpdate,
)
from app.services.equipment_specification_service import EquipmentSpecificationService


router = APIRouter(prefix="/equipment-specifications", tags=["设备规格配置"])


@router.get("", response_model=list[EquipmentSpecificationRead], summary="设备规格列表")
def list_equipment_specifications(db: Session = Depends(get_db)) -> list[EquipmentSpecificationRead]:
    return EquipmentSpecificationService(db).list_specs()


@router.get("/{spec_id}", response_model=EquipmentSpecificationRead, summary="设备规格详情")
def get_equipment_specification(spec_id: int, db: Session = Depends(get_db)) -> EquipmentSpecificationRead:
    return EquipmentSpecificationService(db).get_detail(spec_id)


@router.post(
    "",
    response_model=EquipmentSpecificationRead,
    status_code=status.HTTP_201_CREATED,
    summary="新建设备规格",
)
def create_equipment_specification(
    payload: EquipmentSpecificationCreate, db: Session = Depends(get_db)
) -> EquipmentSpecificationRead:
    return EquipmentSpecificationService(db).create(payload)


@router.put("/{spec_id}", response_model=EquipmentSpecificationRead, summary="更新设备规格")
def update_equipment_specification(
    spec_id: int, payload: EquipmentSpecificationUpdate, db: Session = Depends(get_db)
) -> EquipmentSpecificationRead:
    return EquipmentSpecificationService(db).update(spec_id, payload)


@router.delete("/{spec_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除设备规格")
def delete_equipment_specification(spec_id: int, db: Session = Depends(get_db)) -> Response:
    EquipmentSpecificationService(db).delete(spec_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

