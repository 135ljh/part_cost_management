from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.unit import UnitCreate, UnitRead, UnitUpdate
from app.services.unit_service import UnitService


router = APIRouter(prefix="/units", tags=["单位配置"])


@router.get("", response_model=list[UnitRead], summary="单位列表")
def list_units(db: Session = Depends(get_db)) -> list[UnitRead]:
    return UnitService(db).list_units()


@router.get("/{unit_id}", response_model=UnitRead, summary="单位详情")
def get_unit(unit_id: int, db: Session = Depends(get_db)) -> UnitRead:
    return UnitService(db).get_unit_detail(unit_id)


@router.post("", response_model=UnitRead, status_code=status.HTTP_201_CREATED, summary="新建单位")
def create_unit(payload: UnitCreate, db: Session = Depends(get_db)) -> UnitRead:
    return UnitService(db).create_unit(payload)


@router.put("/{unit_id}", response_model=UnitRead, summary="更新单位")
def update_unit(unit_id: int, payload: UnitUpdate, db: Session = Depends(get_db)) -> UnitRead:
    return UnitService(db).update_unit(unit_id, payload)


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除单位")
def delete_unit(unit_id: int, db: Session = Depends(get_db)) -> Response:
    UnitService(db).delete_unit(unit_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

