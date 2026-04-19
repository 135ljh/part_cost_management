from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.equipment_cost_profile import (
    EquipmentCostProfileCreate,
    EquipmentCostProfileRead,
    EquipmentCostProfileUpdate,
)
from app.services.equipment_cost_profile_service import EquipmentCostProfileService


router = APIRouter(prefix="/equipment-cost-profiles", tags=["设备成本配置"])


@router.get("", response_model=list[EquipmentCostProfileRead], summary="设备成本配置列表")
def list_equipment_cost_profiles(db: Session = Depends(get_db)) -> list[EquipmentCostProfileRead]:
    return EquipmentCostProfileService(db).list_profiles()


@router.get("/{profile_id}", response_model=EquipmentCostProfileRead, summary="设备成本配置详情")
def get_equipment_cost_profile(profile_id: int, db: Session = Depends(get_db)) -> EquipmentCostProfileRead:
    return EquipmentCostProfileService(db).get_detail(profile_id)


@router.post(
    "",
    response_model=EquipmentCostProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="新建设备成本配置",
)
def create_equipment_cost_profile(
    payload: EquipmentCostProfileCreate, db: Session = Depends(get_db)
) -> EquipmentCostProfileRead:
    return EquipmentCostProfileService(db).create(payload)


@router.put("/{profile_id}", response_model=EquipmentCostProfileRead, summary="更新设备成本配置")
def update_equipment_cost_profile(
    profile_id: int, payload: EquipmentCostProfileUpdate, db: Session = Depends(get_db)
) -> EquipmentCostProfileRead:
    return EquipmentCostProfileService(db).update(profile_id, payload)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除设备成本配置")
def delete_equipment_cost_profile(profile_id: int, db: Session = Depends(get_db)) -> Response:
    EquipmentCostProfileService(db).delete(profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

