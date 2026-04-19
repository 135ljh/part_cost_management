from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.bom import BomItemCreateGlobal, BomItemRead, BomItemUpdate
from app.services.bom_service import BomService


router = APIRouter(prefix="/bom-items", tags=["BOM明细管理"])


@router.get("", response_model=list[BomItemRead], summary="BOM明细列表")
def list_bom_items(db: Session = Depends(get_db)) -> list[BomItemRead]:
    return BomService(db).list_all_items()


@router.get("/{item_id}", response_model=BomItemRead, summary="BOM明细详情")
def get_bom_item(item_id: int, db: Session = Depends(get_db)) -> BomItemRead:
    return BomService(db).get_item_detail(item_id)


@router.post("", response_model=BomItemRead, status_code=status.HTTP_201_CREATED, summary="新建BOM明细")
def create_bom_item(payload: BomItemCreateGlobal, db: Session = Depends(get_db)) -> BomItemRead:
    return BomService(db).create_item_global(payload)


@router.put("/{item_id}", response_model=BomItemRead, summary="更新BOM明细")
def update_bom_item(item_id: int, payload: BomItemUpdate, db: Session = Depends(get_db)) -> BomItemRead:
    return BomService(db).update_item_global(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除BOM明细")
def delete_bom_item(item_id: int, db: Session = Depends(get_db)) -> Response:
    BomService(db).delete_item_global(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

