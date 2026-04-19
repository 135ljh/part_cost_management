from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RegionCostProfileBase(BaseModel):
    profile_name: str = Field(..., max_length=128, description="配置名称")
    region_id: int = Field(..., gt=0, description="所属区域ID")
    supplier_name: Optional[str] = Field(None, max_length=128, description="工厂名称")
    supplier_code: Optional[str] = Field(None, max_length=64, description="工厂编号")
    currency_id: int = Field(..., gt=0, description="基础货币ID")
    operating_worker_rate: Decimal = Field(Decimal("0"), ge=0)
    skilled_worker_rate: Decimal = Field(Decimal("0"), ge=0)
    transfer_technician_rate: Decimal = Field(Decimal("0"), ge=0)
    production_leader_rate: Decimal = Field(Decimal("0"), ge=0)
    inspector_rate: Decimal = Field(Decimal("0"), ge=0)
    engineer_rate: Decimal = Field(Decimal("0"), ge=0)
    mold_fitter_rate: Decimal = Field(Decimal("0"), ge=0)
    cost_interest_rate: Decimal = Field(Decimal("0"), ge=0)
    benefits_one_shift: Decimal = Field(Decimal("0"), ge=0)
    benefits_two_shift: Decimal = Field(Decimal("0"), ge=0)
    benefits_three_shift: Decimal = Field(Decimal("0"), ge=0)
    factory_rent: Decimal = Field(Decimal("0"), ge=0)
    office_fee: Decimal = Field(Decimal("0"), ge=0)
    electricity_fee: Decimal = Field(Decimal("0"), ge=0)
    water_fee: Decimal = Field(Decimal("0"), ge=0)
    gas_fee: Decimal = Field(Decimal("0"), ge=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: bool = True
    remark: Optional[str] = Field(None, max_length=255)


class RegionCostProfileCreate(RegionCostProfileBase):
    profile_code: Optional[str] = Field(None, max_length=64, description="配置编码")


class RegionCostProfileUpdate(BaseModel):
    profile_name: Optional[str] = Field(None, max_length=128)
    region_id: Optional[int] = Field(None, gt=0)
    supplier_name: Optional[str] = Field(None, max_length=128)
    supplier_code: Optional[str] = Field(None, max_length=64)
    currency_id: Optional[int] = Field(None, gt=0)
    operating_worker_rate: Optional[Decimal] = Field(None, ge=0)
    skilled_worker_rate: Optional[Decimal] = Field(None, ge=0)
    transfer_technician_rate: Optional[Decimal] = Field(None, ge=0)
    production_leader_rate: Optional[Decimal] = Field(None, ge=0)
    inspector_rate: Optional[Decimal] = Field(None, ge=0)
    engineer_rate: Optional[Decimal] = Field(None, ge=0)
    mold_fitter_rate: Optional[Decimal] = Field(None, ge=0)
    cost_interest_rate: Optional[Decimal] = Field(None, ge=0)
    benefits_one_shift: Optional[Decimal] = Field(None, ge=0)
    benefits_two_shift: Optional[Decimal] = Field(None, ge=0)
    benefits_three_shift: Optional[Decimal] = Field(None, ge=0)
    factory_rent: Optional[Decimal] = Field(None, ge=0)
    office_fee: Optional[Decimal] = Field(None, ge=0)
    electricity_fee: Optional[Decimal] = Field(None, ge=0)
    water_fee: Optional[Decimal] = Field(None, ge=0)
    gas_fee: Optional[Decimal] = Field(None, ge=0)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class RegionCostProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_code: str
    profile_name: str
    region_id: int
    supplier_name: Optional[str]
    supplier_code: Optional[str]
    currency_id: int
    operating_worker_rate: Decimal
    skilled_worker_rate: Decimal
    transfer_technician_rate: Decimal
    production_leader_rate: Decimal
    inspector_rate: Decimal
    engineer_rate: Decimal
    mold_fitter_rate: Decimal
    cost_interest_rate: Decimal
    benefits_one_shift: Decimal
    benefits_two_shift: Decimal
    benefits_three_shift: Decimal
    factory_rent: Decimal
    office_fee: Decimal
    electricity_fee: Decimal
    water_fee: Decimal
    gas_fee: Decimal
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    street: Optional[str] = None
    factory_name: Optional[str] = None
    factory_code: Optional[str] = None

