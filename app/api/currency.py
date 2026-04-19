from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.currency import CurrencyCreate, CurrencyRead, CurrencyUpdate
from app.services.currency_service import CurrencyService


router = APIRouter(prefix="/currencies", tags=["货币配置"])


@router.get("", response_model=list[CurrencyRead], summary="货币列表")
def list_currencies(db: Session = Depends(get_db)) -> list[CurrencyRead]:
    return CurrencyService(db).list_currencies()


@router.get("/{currency_id}", response_model=CurrencyRead, summary="货币详情")
def get_currency(currency_id: int, db: Session = Depends(get_db)) -> CurrencyRead:
    return CurrencyService(db).get_currency_detail(currency_id)


@router.post(
    "", response_model=CurrencyRead, status_code=status.HTTP_201_CREATED, summary="新建货币"
)
def create_currency(payload: CurrencyCreate, db: Session = Depends(get_db)) -> CurrencyRead:
    return CurrencyService(db).create_currency(payload)


@router.put("/{currency_id}", response_model=CurrencyRead, summary="更新货币")
def update_currency(
    currency_id: int, payload: CurrencyUpdate, db: Session = Depends(get_db)
) -> CurrencyRead:
    return CurrencyService(db).update_currency(currency_id, payload)


@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除货币")
def delete_currency(currency_id: int, db: Session = Depends(get_db)) -> Response:
    CurrencyService(db).delete_currency(currency_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

