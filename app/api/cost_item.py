from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.cost_item import CostCalcRequest, CostItemCreate, CostItemRead, CostItemUpdate
from app.services.cost_item_service import CostItemService


router = APIRouter(prefix="/cost-items", tags=["零件成本计算"])


@router.get("", response_model=list[CostItemRead], summary="成本计算列表")
def list_cost_items(db: Session = Depends(get_db)) -> list[CostItemRead]:
    return CostItemService(db).list_items()


@router.get("/part/{part_id}/latest", response_model=CostItemRead, summary="零件最新成本")
def get_part_latest_cost(part_id: int, db: Session = Depends(get_db)) -> CostItemRead:
    return CostItemService(db).get_latest_by_part(part_id)


@router.get("/{item_id}", response_model=CostItemRead, summary="成本计算详情")
def get_cost_item(item_id: int, db: Session = Depends(get_db)) -> CostItemRead:
    return CostItemService(db).get_detail(item_id)


@router.post("", response_model=CostItemRead, status_code=status.HTTP_201_CREATED, summary="新建成本记录")
def create_cost_item(payload: CostItemCreate, db: Session = Depends(get_db)) -> CostItemRead:
    return CostItemService(db).create(payload)


@router.post(
    "/part/{part_id}/calculate",
    response_model=CostItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="执行零件成本计算(材料成本阶段)",
)
def calculate_part_cost(part_id: int, payload: CostCalcRequest, db: Session = Depends(get_db)) -> CostItemRead:
    return CostItemService(db).calculate_for_part(part_id, payload)


@router.put("/{item_id}", response_model=CostItemRead, summary="更新成本记录")
def update_cost_item(item_id: int, payload: CostItemUpdate, db: Session = Depends(get_db)) -> CostItemRead:
    return CostItemService(db).update(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除成本记录")
def delete_cost_item(item_id: int, db: Session = Depends(get_db)) -> Response:
    CostItemService(db).delete(item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
