from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.bom import (
    BomCreate,
    BomItemCreate,
    BomItemRead,
    BomItemUpdate,
    BomRead,
    BomUpdate,
    PartBomDetailRead,
)
from app.services.bom_service import BomService


router = APIRouter(prefix="/boms", tags=["BOM管理"])


@router.get("", response_model=list[BomRead], summary="BOM列表")
def list_boms(db: Session = Depends(get_db)) -> list[BomRead]:
    return BomService(db).list_boms()


@router.get("/part/{part_id}/detail", response_model=PartBomDetailRead, summary="按零件查看BOM详情")
def get_part_bom_detail(part_id: int, db: Session = Depends(get_db)) -> PartBomDetailRead:
    part, bom, items = BomService(db).get_part_bom_detail(part_id)
    return PartBomDetailRead(
        part_id=part.id,
        part_code=part.part_code,
        part_name=part.part_name,
        bom=bom,
        items=items,
    )


@router.get("/{bom_id}", response_model=BomRead, summary="BOM详情")
def get_bom(bom_id: int, db: Session = Depends(get_db)) -> BomRead:
    return BomService(db).get_bom(bom_id)


@router.post("", response_model=BomRead, status_code=status.HTTP_201_CREATED, summary="新建BOM")
def create_bom(payload: BomCreate, db: Session = Depends(get_db)) -> BomRead:
    return BomService(db).create_bom(payload)


@router.put("/{bom_id}", response_model=BomRead, summary="更新BOM")
def update_bom(bom_id: int, payload: BomUpdate, db: Session = Depends(get_db)) -> BomRead:
    return BomService(db).update_bom(bom_id, payload)


@router.delete("/{bom_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除BOM")
def delete_bom(bom_id: int, db: Session = Depends(get_db)) -> Response:
    BomService(db).delete_bom(bom_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{bom_id}/items", response_model=list[BomItemRead], summary="BOM明细列表")
def list_bom_items(bom_id: int, db: Session = Depends(get_db)) -> list[BomItemRead]:
    return BomService(db).list_items(bom_id)


@router.post(
    "/{bom_id}/items",
    response_model=BomItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="新增BOM明细",
)
def create_bom_item(bom_id: int, payload: BomItemCreate, db: Session = Depends(get_db)) -> BomItemRead:
    return BomService(db).create_item(bom_id, payload)


@router.put("/{bom_id}/items/{item_id}", response_model=BomItemRead, summary="更新BOM明细")
def update_bom_item(
    bom_id: int, item_id: int, payload: BomItemUpdate, db: Session = Depends(get_db)
) -> BomItemRead:
    return BomService(db).update_item(bom_id, item_id, payload)


@router.delete("/{bom_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除BOM明细")
def delete_bom_item(bom_id: int, item_id: int, db: Session = Depends(get_db)) -> Response:
    BomService(db).delete_item(bom_id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

