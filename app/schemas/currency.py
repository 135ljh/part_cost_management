from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CurrencyBase(BaseModel):
    currency_code: str = Field(..., min_length=3, max_length=16, description="ISO代码")
    currency_name: str = Field(..., max_length=64, description="名称")
    currency_symbol: Optional[str] = Field(None, max_length=16, description="符号")
    precision_scale: int = Field(2, ge=0, le=8, description="金额精度")
    is_base_currency: bool = Field(False, description="是否基准货币")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    currency_code: Optional[str] = Field(None, min_length=3, max_length=16)
    currency_name: Optional[str] = Field(None, max_length=64)
    currency_symbol: Optional[str] = Field(None, max_length=16)
    precision_scale: Optional[int] = Field(None, ge=0, le=8)
    is_base_currency: Optional[bool] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class CurrencyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    currency_code: str
    currency_name: str
    currency_symbol: Optional[str]
    precision_scale: int
    is_base_currency: bool
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

