from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate
from app.services.equipment_service import EquipmentService


router = APIRouter(prefix="/equipment", tags=["设备配置"])


@router.get("", response_model=list[EquipmentRead], summary="设备列表")
def list_equipment(db: Session = Depends(get_db)) -> list[EquipmentRead]:
    return EquipmentService(db).list_equipment()


@router.get("/{equipment_id}", response_model=EquipmentRead, summary="设备详情")
def get_equipment(equipment_id: int, db: Session = Depends(get_db)) -> EquipmentRead:
    return EquipmentService(db).get_detail(equipment_id)


@router.post("", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED, summary="新建设备")
def create_equipment(payload: EquipmentCreate, db: Session = Depends(get_db)) -> EquipmentRead:
    return EquipmentService(db).create(payload)


@router.put("/{equipment_id}", response_model=EquipmentRead, summary="更新设备")
def update_equipment(
    equipment_id: int, payload: EquipmentUpdate, db: Session = Depends(get_db)
) -> EquipmentRead:
    return EquipmentService(db).update(equipment_id, payload)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除设备")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)) -> Response:
    EquipmentService(db).delete(equipment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

