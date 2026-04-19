from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.equipment_rate import EquipmentRateCreate, EquipmentRateRead, EquipmentRateUpdate
from app.services.equipment_rate_service import EquipmentRateService


router = APIRouter(prefix="/equipment-rates", tags=["设备费率配置"])


@router.get("", response_model=list[EquipmentRateRead], summary="设备费率列表")
def list_equipment_rates(db: Session = Depends(get_db)) -> list[EquipmentRateRead]:
    return EquipmentRateService(db).list_rates()


@router.get("/{rate_id}", response_model=EquipmentRateRead, summary="设备费率详情")
def get_equipment_rate(rate_id: int, db: Session = Depends(get_db)) -> EquipmentRateRead:
    return EquipmentRateService(db).get_rate_detail(rate_id)


@router.post(
    "",
    response_model=EquipmentRateRead,
    status_code=status.HTTP_201_CREATED,
    summary="新建设备费率",
)
def create_equipment_rate(payload: EquipmentRateCreate, db: Session = Depends(get_db)) -> EquipmentRateRead:
    return EquipmentRateService(db).create_rate(payload)


@router.put("/{rate_id}", response_model=EquipmentRateRead, summary="更新设备费率")
def update_equipment_rate(
    rate_id: int, payload: EquipmentRateUpdate, db: Session = Depends(get_db)
) -> EquipmentRateRead:
    return EquipmentRateService(db).update_rate(rate_id, payload)


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除设备费率")
def delete_equipment_rate(rate_id: int, db: Session = Depends(get_db)) -> Response:
    EquipmentRateService(db).delete_rate(rate_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

