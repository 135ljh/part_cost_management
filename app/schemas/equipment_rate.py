from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EquipmentRateBase(BaseModel):
    equipment_id: Optional[int] = Field(None, gt=0, description="设备ID")
    equipment_number: Optional[str] = Field(None, max_length=64, description="设备编号")
    equipment_category_id: Optional[int] = Field(None, gt=0, description="设备类别ID")
    equipment_category_name: Optional[str] = Field(None, max_length=128, description="设备类别")
    description: Optional[str] = Field(None, max_length=255)
    equipment_type: Optional[str] = Field(None, max_length=64)
    manpower: int = Field(0, ge=0)
    labor_group: Optional[str] = Field(None, max_length=64)
    direct_labor: Decimal = Field(Decimal("0"), ge=0)
    direct_fringe: Decimal = Field(Decimal("0"), ge=0)
    indirect_labor: Decimal = Field(Decimal("0"), ge=0)
    indirect_fringe: Decimal = Field(Decimal("0"), ge=0)
    total_labor: Decimal = Field(Decimal("0"), ge=0)
    depreciation: Decimal = Field(Decimal("0"), ge=0)
    insurance: Decimal = Field(Decimal("0"), ge=0)
    floor_space: Decimal = Field(Decimal("0"), ge=0)
    mro_labor: Decimal = Field(Decimal("0"), ge=0)
    utilities: Decimal = Field(Decimal("0"), ge=0)
    indirect_materials: Decimal = Field(Decimal("0"), ge=0)
    other_burden: Decimal = Field(Decimal("0"), ge=0)
    total_burden: Decimal = Field(Decimal("0"), ge=0)
    total_minute_rate: Decimal = Field(Decimal("0"), ge=0)
    investment: Decimal = Field(Decimal("0"), ge=0)
    currency_id: Optional[int] = Field(None, gt=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: bool = True
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentRateCreate(EquipmentRateBase):
    rate_code: Optional[str] = Field(None, max_length=64, description="费率编码")


class EquipmentRateUpdate(BaseModel):
    equipment_id: Optional[int] = Field(None, gt=0)
    equipment_number: Optional[str] = Field(None, max_length=64)
    equipment_category_id: Optional[int] = Field(None, gt=0)
    equipment_category_name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=255)
    equipment_type: Optional[str] = Field(None, max_length=64)
    manpower: Optional[int] = Field(None, ge=0)
    labor_group: Optional[str] = Field(None, max_length=64)
    direct_labor: Optional[Decimal] = Field(None, ge=0)
    direct_fringe: Optional[Decimal] = Field(None, ge=0)
    indirect_labor: Optional[Decimal] = Field(None, ge=0)
    indirect_fringe: Optional[Decimal] = Field(None, ge=0)
    total_labor: Optional[Decimal] = Field(None, ge=0)
    depreciation: Optional[Decimal] = Field(None, ge=0)
    insurance: Optional[Decimal] = Field(None, ge=0)
    floor_space: Optional[Decimal] = Field(None, ge=0)
    mro_labor: Optional[Decimal] = Field(None, ge=0)
    utilities: Optional[Decimal] = Field(None, ge=0)
    indirect_materials: Optional[Decimal] = Field(None, ge=0)
    other_burden: Optional[Decimal] = Field(None, ge=0)
    total_burden: Optional[Decimal] = Field(None, ge=0)
    total_minute_rate: Optional[Decimal] = Field(None, ge=0)
    investment: Optional[Decimal] = Field(None, ge=0)
    currency_id: Optional[int] = Field(None, gt=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentRateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rate_code: str
    equipment_id: Optional[int]
    equipment_number: Optional[str] = None
    equipment_category_id: Optional[int]
    equipment_category_name: Optional[str] = None
    description: Optional[str]
    equipment_type: Optional[str]
    manpower: int
    labor_group: Optional[str]
    direct_labor: Decimal
    direct_fringe: Decimal
    indirect_labor: Decimal
    indirect_fringe: Decimal
    total_labor: Decimal
    depreciation: Decimal
    insurance: Decimal
    floor_space: Decimal
    mro_labor: Decimal
    utilities: Decimal
    indirect_materials: Decimal
    other_burden: Decimal
    total_burden: Decimal
    total_minute_rate: Decimal
    investment: Decimal
    currency_id: Optional[int]
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

