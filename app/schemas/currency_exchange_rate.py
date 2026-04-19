from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


RateType = Literal["REALTIME", "FIXED", "MANUAL"]


class CurrencyExchangeRateBase(BaseModel):
    from_currency_id: int = Field(..., gt=0, description="源货币ID")
    to_currency_id: int = Field(..., gt=0, description="目标货币ID")
    rate_type: RateType = Field(..., description="汇率类型")
    exchange_rate: Decimal = Field(..., gt=0, description="汇率值")
    effective_date: datetime = Field(..., description="生效时间")
    source_name: Optional[str] = Field(None, max_length=128, description="数据来源")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class CurrencyExchangeRateCreate(CurrencyExchangeRateBase):
    pass


class CurrencyExchangeRateUpdate(BaseModel):
    from_currency_id: Optional[int] = Field(None, gt=0)
    to_currency_id: Optional[int] = Field(None, gt=0)
    rate_type: Optional[RateType] = None
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    effective_date: Optional[datetime] = None
    source_name: Optional[str] = Field(None, max_length=128)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class CurrencyExchangeRateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_currency_id: int
    to_currency_id: int
    rate_type: RateType
    exchange_rate: Decimal
    effective_date: datetime
    source_name: Optional[str]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

