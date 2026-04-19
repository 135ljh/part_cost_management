from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.part import PartCreate, PartRead, PartUpdate
from app.services.part_service import PartService


router = APIRouter(prefix="/parts", tags=["零件主数据"])


@router.get("", response_model=list[PartRead], summary="零件列表")
def list_parts(db: Session = Depends(get_db)) -> list[PartRead]:
    return PartService(db).list_parts()


@router.get("/{part_id}", response_model=PartRead, summary="零件详情")
def get_part(part_id: int, db: Session = Depends(get_db)) -> PartRead:
    return PartService(db).get_part_detail(part_id)


@router.post("", response_model=PartRead, status_code=status.HTTP_201_CREATED, summary="新建零件")
def create_part(payload: PartCreate, db: Session = Depends(get_db)) -> PartRead:
    return PartService(db).create_part(payload)


@router.put("/{part_id}", response_model=PartRead, summary="更新零件")
def update_part(part_id: int, payload: PartUpdate, db: Session = Depends(get_db)) -> PartRead:
    return PartService(db).update_part(part_id, payload)


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除零件")
def delete_part(part_id: int, db: Session = Depends(get_db)) -> Response:
    PartService(db).delete_part(part_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
