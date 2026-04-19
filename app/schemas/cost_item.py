from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CostItemBase(BaseModel):
    calculation_name: str = Field(..., max_length=128, description="Calculation name")
    part_id: int = Field(..., gt=0, description="Part ID")
    currency_id: int = Field(..., gt=0, description="Currency ID")
    unit_id: Optional[int] = Field(None, gt=0, description="Unit ID")
    material_cost: Decimal = Field(Decimal("0"), description="Material cost")
    manufacturing_cost: Decimal = Field(Decimal("0"), description="Manufacturing cost")
    overhead_cost: Decimal = Field(Decimal("0"), description="Overhead cost")
    total_cost: Decimal = Field(Decimal("0"), description="Total cost")
    rule_version: str = Field("material_v1", max_length=32, description="Rule version")
    trace_detail: Optional[str] = Field(None, description="Trace detail JSON")
    remark: Optional[str] = Field(None, max_length=255, description="Remark")


class CostItemCreate(CostItemBase):
    pass


class CostItemUpdate(BaseModel):
    calculation_name: Optional[str] = Field(None, max_length=128)
    part_id: Optional[int] = Field(None, gt=0)
    currency_id: Optional[int] = Field(None, gt=0)
    unit_id: Optional[int] = Field(None, gt=0)
    material_cost: Optional[Decimal] = None
    manufacturing_cost: Optional[Decimal] = None
    overhead_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    rule_version: Optional[str] = Field(None, max_length=32)
    trace_detail: Optional[str] = None
    remark: Optional[str] = Field(None, max_length=255)


class CostItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    calculation_name: str
    part_id: int
    part_code: Optional[str]
    part_name: Optional[str]
    currency_id: int
    currency_code: Optional[str]
    unit_id: Optional[int]
    unit_code: Optional[str]
    material_cost: Decimal
    manufacturing_cost: Decimal
    overhead_cost: Decimal
    total_cost: Decimal
    rule_version: str
    trace_detail: Optional[str]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime


class CostCalcRequest(BaseModel):
    # base
    calculation_name: Optional[str] = Field(None, max_length=128)
    currency_id: Optional[int] = Field(None, gt=0)
    unit_id: Optional[int] = Field(None, gt=0)
    remark: Optional[str] = Field(None, max_length=255)

    # material calculator inputs
    theoretical_feed_weight: Optional[Decimal] = Field(None, ge=0, description="理论投料重量")
    feed_loss_rate: Decimal = Field(Decimal("0"), ge=0, description="投料损失(%)")
    net_weight: Optional[Decimal] = Field(None, ge=0, description="净重")
    material_unit_price: Optional[Decimal] = Field(None, ge=0, description="材料单位基价")
    waste_income_price: Decimal = Field(Decimal("0"), ge=0, description="废料收入单价")
    waste_expense_price: Decimal = Field(Decimal("0"), ge=0, description="废料支出单价")

    # other material costs
    material_scrap_cost: Decimal = Field(Decimal("0"), ge=0, description="材料报废成本")
    indirect_material_cost: Decimal = Field(Decimal("0"), ge=0, description="材料间接费用")
    material_inventory_interest: Decimal = Field(Decimal("0"), ge=0, description="材料库存利息")
