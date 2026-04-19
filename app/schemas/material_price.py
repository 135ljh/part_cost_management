from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MaterialPriceBase(BaseModel):
    material_id: int = Field(..., gt=0)
    region_id: Optional[int] = Field(None, gt=0)
    supplier_name: Optional[str] = Field(None, max_length=128)
    currency_id: int = Field(..., gt=0)
    price_unit_id: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    source_name: Optional[str] = Field(None, max_length=128)
    is_active: bool = True
    remark: Optional[str] = Field(None, max_length=255)


class MaterialPriceCreate(MaterialPriceBase):
    pass


class MaterialPriceUpdate(BaseModel):
    material_id: Optional[int] = Field(None, gt=0)
    region_id: Optional[int] = Field(None, gt=0)
    supplier_name: Optional[str] = Field(None, max_length=128)
    currency_id: Optional[int] = Field(None, gt=0)
    price_unit_id: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    source_name: Optional[str] = Field(None, max_length=128)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class MaterialPriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    region_id: Optional[int]
    supplier_name: Optional[str]
    currency_id: int
    price_unit_id: int
    unit_price: Decimal
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    source_name: Optional[str]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

