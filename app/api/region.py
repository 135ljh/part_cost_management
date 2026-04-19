from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.region import RegionCreate, RegionRead, RegionUpdate
from app.services.region_service import RegionService


router = APIRouter(prefix="/regions", tags=["区域配置"])


@router.get("", response_model=list[RegionRead], summary="区域列表")
def list_regions(db: Session = Depends(get_db)) -> list[RegionRead]:
    return RegionService(db).list_regions()


@router.get("/{region_id}", response_model=RegionRead, summary="区域详情")
def get_region(region_id: int, db: Session = Depends(get_db)) -> RegionRead:
    return RegionService(db).get_region_detail(region_id)


@router.post("", response_model=RegionRead, status_code=status.HTTP_201_CREATED, summary="新建区域")
def create_region(payload: RegionCreate, db: Session = Depends(get_db)) -> RegionRead:
    return RegionService(db).create_region(payload)


@router.put("/{region_id}", response_model=RegionRead, summary="更新区域")
def update_region(region_id: int, payload: RegionUpdate, db: Session = Depends(get_db)) -> RegionRead:
    return RegionService(db).update_region(region_id, payload)


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除区域")
def delete_region(region_id: int, db: Session = Depends(get_db)) -> Response:
    RegionService(db).delete_region(region_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

