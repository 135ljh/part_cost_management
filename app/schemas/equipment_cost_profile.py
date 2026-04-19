from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EquipmentCostProfileBase(BaseModel):
    equipment_id: int = Field(..., gt=0)
    profile_name: str = Field(..., max_length=128)
    equipment_number_snapshot: Optional[str] = Field(None, max_length=64)
    manufacturer_snapshot: Optional[str] = Field(None, max_length=128)
    technical_reliability: Decimal = Field(Decimal("0"), ge=0)
    currency_id: int = Field(..., gt=0)
    acquisition_value: Decimal = Field(Decimal("0"), ge=0)
    number_of_equipment: Decimal = Field(Decimal("1"), ge=0)
    annual_production_hours: Decimal = Field(Decimal("0"), ge=0)
    equipment_efficiency: Decimal = Field(Decimal("0"), ge=0)
    installation_expenses: Decimal = Field(Decimal("0"), ge=0)
    foundation_expenses: Decimal = Field(Decimal("0"), ge=0)
    other_expenses: Decimal = Field(Decimal("0"), ge=0)
    residual_value: Decimal = Field(Decimal("0"), ge=0)
    equipment_lifespan_years: Decimal = Field(Decimal("0"), ge=0)
    estimated_depreciation: Decimal = Field(Decimal("0"), ge=0)
    interest_rate: Decimal = Field(Decimal("0"), ge=0)
    total_area_required: Decimal = Field(Decimal("0"), ge=0)
    production_site_cost: Decimal = Field(Decimal("0"), ge=0)
    rated_power: Decimal = Field(Decimal("0"), ge=0)
    electricity_usage_ratio: Decimal = Field(Decimal("0"), ge=0)
    power_cost_electricity: Decimal = Field(Decimal("0"), ge=0)
    maintenance_cost: Decimal = Field(Decimal("0"), ge=0)
    auxiliary_material_cost: Decimal = Field(Decimal("0"), ge=0)
    total_fixed_cost: Decimal = Field(Decimal("0"), ge=0)
    total_variable_cost: Decimal = Field(Decimal("0"), ge=0)
    cost_per_unit_time: Decimal = Field(Decimal("0"), ge=0)
    hourly_rate: Decimal = Field(Decimal("0"), ge=0)
    equipment_cost: Decimal = Field(Decimal("0"), ge=0)
    investment: Decimal = Field(Decimal("0"), ge=0)
    asset_status: Optional[str] = Field(None, max_length=32)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: bool = True
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentCostProfileCreate(EquipmentCostProfileBase):
    pass


class EquipmentCostProfileUpdate(BaseModel):
    equipment_id: Optional[int] = Field(None, gt=0)
    profile_name: Optional[str] = Field(None, max_length=128)
    equipment_number_snapshot: Optional[str] = Field(None, max_length=64)
    manufacturer_snapshot: Optional[str] = Field(None, max_length=128)
    technical_reliability: Optional[Decimal] = Field(None, ge=0)
    currency_id: Optional[int] = Field(None, gt=0)
    acquisition_value: Optional[Decimal] = Field(None, ge=0)
    number_of_equipment: Optional[Decimal] = Field(None, ge=0)
    annual_production_hours: Optional[Decimal] = Field(None, ge=0)
    equipment_efficiency: Optional[Decimal] = Field(None, ge=0)
    installation_expenses: Optional[Decimal] = Field(None, ge=0)
    foundation_expenses: Optional[Decimal] = Field(None, ge=0)
    other_expenses: Optional[Decimal] = Field(None, ge=0)
    residual_value: Optional[Decimal] = Field(None, ge=0)
    equipment_lifespan_years: Optional[Decimal] = Field(None, ge=0)
    estimated_depreciation: Optional[Decimal] = Field(None, ge=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0)
    total_area_required: Optional[Decimal] = Field(None, ge=0)
    production_site_cost: Optional[Decimal] = Field(None, ge=0)
    rated_power: Optional[Decimal] = Field(None, ge=0)
    electricity_usage_ratio: Optional[Decimal] = Field(None, ge=0)
    power_cost_electricity: Optional[Decimal] = Field(None, ge=0)
    maintenance_cost: Optional[Decimal] = Field(None, ge=0)
    auxiliary_material_cost: Optional[Decimal] = Field(None, ge=0)
    total_fixed_cost: Optional[Decimal] = Field(None, ge=0)
    total_variable_cost: Optional[Decimal] = Field(None, ge=0)
    cost_per_unit_time: Optional[Decimal] = Field(None, ge=0)
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    equipment_cost: Optional[Decimal] = Field(None, ge=0)
    investment: Optional[Decimal] = Field(None, ge=0)
    asset_status: Optional[str] = Field(None, max_length=32)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentCostProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: int
    profile_name: str
    equipment_number_snapshot: Optional[str]
    manufacturer_snapshot: Optional[str]
    technical_reliability: Decimal
    currency_id: int
    acquisition_value: Decimal
    number_of_equipment: Decimal
    annual_production_hours: Decimal
    equipment_efficiency: Decimal
    installation_expenses: Decimal
    foundation_expenses: Decimal
    other_expenses: Decimal
    residual_value: Decimal
    equipment_lifespan_years: Decimal
    estimated_depreciation: Decimal
    interest_rate: Decimal
    total_area_required: Decimal
    production_site_cost: Decimal
    rated_power: Decimal
    electricity_usage_ratio: Decimal
    power_cost_electricity: Decimal
    maintenance_cost: Decimal
    auxiliary_material_cost: Decimal
    total_fixed_cost: Decimal
    total_variable_cost: Decimal
    cost_per_unit_time: Decimal
    hourly_rate: Decimal
    equipment_cost: Decimal
    investment: Decimal
    asset_status: Optional[str]
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

