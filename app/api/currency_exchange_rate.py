from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.currency_exchange_rate import (
    CurrencyExchangeRateCreate,
    CurrencyExchangeRateRead,
    CurrencyExchangeRateUpdate,
)
from app.services.currency_exchange_rate_service import CurrencyExchangeRateService


router = APIRouter(prefix="/exchange-rates", tags=["汇率配置"])


@router.get("", response_model=list[CurrencyExchangeRateRead], summary="汇率列表")
def list_exchange_rates(db: Session = Depends(get_db)) -> list[CurrencyExchangeRateRead]:
    return CurrencyExchangeRateService(db).list_rates()


@router.get("/{rate_id}", response_model=CurrencyExchangeRateRead, summary="汇率详情")
def get_exchange_rate(rate_id: int, db: Session = Depends(get_db)) -> CurrencyExchangeRateRead:
    return CurrencyExchangeRateService(db).get_rate_detail(rate_id)


@router.post(
    "",
    response_model=CurrencyExchangeRateRead,
    status_code=status.HTTP_201_CREATED,
    summary="新建汇率",
)
def create_exchange_rate(
    payload: CurrencyExchangeRateCreate, db: Session = Depends(get_db)
) -> CurrencyExchangeRateRead:
    return CurrencyExchangeRateService(db).create_rate(payload)


@router.put("/{rate_id}", response_model=CurrencyExchangeRateRead, summary="更新汇率")
def update_exchange_rate(
    rate_id: int, payload: CurrencyExchangeRateUpdate, db: Session = Depends(get_db)
) -> CurrencyExchangeRateRead:
    return CurrencyExchangeRateService(db).update_rate(rate_id, payload)


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除汇率")
def delete_exchange_rate(rate_id: int, db: Session = Depends(get_db)) -> Response:
    CurrencyExchangeRateService(db).delete_rate(rate_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

