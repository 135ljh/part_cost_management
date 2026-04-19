from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_price import MaterialPriceCreate, MaterialPriceRead, MaterialPriceUpdate
from app.services.material_price_service import MaterialPriceService


router = APIRouter(prefix="/material-prices", tags=["物质价格配置"])


@router.get("", response_model=list[MaterialPriceRead], summary="物质价格列表")
def list_material_prices(db: Session = Depends(get_db)) -> list[MaterialPriceRead]:
    return MaterialPriceService(db).list_prices()


@router.get("/{price_id}", response_model=MaterialPriceRead, summary="物质价格详情")
def get_material_price(price_id: int, db: Session = Depends(get_db)) -> MaterialPriceRead:
    return MaterialPriceService(db).get_detail(price_id)


@router.post("", response_model=MaterialPriceRead, status_code=status.HTTP_201_CREATED, summary="新建物质价格")
def create_material_price(
    payload: MaterialPriceCreate, db: Session = Depends(get_db)
) -> MaterialPriceRead:
    return MaterialPriceService(db).create(payload)


@router.put("/{price_id}", response_model=MaterialPriceRead, summary="更新物质价格")
def update_material_price(
    price_id: int, payload: MaterialPriceUpdate, db: Session = Depends(get_db)
) -> MaterialPriceRead:
    return MaterialPriceService(db).update(price_id, payload)


@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除物质价格")
def delete_material_price(price_id: int, db: Session = Depends(get_db)) -> Response:
    MaterialPriceService(db).delete(price_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

