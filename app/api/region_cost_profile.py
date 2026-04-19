from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.region_cost_profile import (
    RegionCostProfileCreate,
    RegionCostProfileRead,
    RegionCostProfileUpdate,
)
from app.services.region_cost_profile_service import RegionCostProfileService


router = APIRouter(prefix="/region-cost-profiles", tags=["区域成本配置"])


@router.get("", response_model=list[RegionCostProfileRead], summary="区域成本配置列表")
def list_region_cost_profiles(db: Session = Depends(get_db)) -> list[RegionCostProfileRead]:
    return RegionCostProfileService(db).list_profiles()


@router.get("/{profile_id}", response_model=RegionCostProfileRead, summary="区域成本配置详情")
def get_region_cost_profile(profile_id: int, db: Session = Depends(get_db)) -> RegionCostProfileRead:
    return RegionCostProfileService(db).get_profile_detail(profile_id)


@router.post(
    "",
    response_model=RegionCostProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="新建区域成本配置",
)
def create_region_cost_profile(
    payload: RegionCostProfileCreate, db: Session = Depends(get_db)
) -> RegionCostProfileRead:
    return RegionCostProfileService(db).create_profile(payload)


@router.put("/{profile_id}", response_model=RegionCostProfileRead, summary="更新区域成本配置")
def update_region_cost_profile(
    profile_id: int, payload: RegionCostProfileUpdate, db: Session = Depends(get_db)
) -> RegionCostProfileRead:
    return RegionCostProfileService(db).update_profile(profile_id, payload)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除区域成本配置")
def delete_region_cost_profile(profile_id: int, db: Session = Depends(get_db)) -> Response:
    RegionCostProfileService(db).delete_profile(profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

