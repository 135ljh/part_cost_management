from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):
    unit_code: str = Field(..., max_length=32, description="单位编码")
    unit_name: str = Field(..., max_length=64, description="单位名称")
    unit_display_name: Optional[str] = Field(None, max_length=64, description="显示名")
    unit_category: str = Field(..., max_length=64, description="单位类别")
    measurement_system: Optional[str] = Field(None, max_length=64, description="度量系统")
    base_unit_id: Optional[int] = Field(None, description="基准单位ID")
    unit_factor: Decimal = Field(..., ge=0, description="换算系数")
    sync_time: Optional[datetime] = Field(None, description="同步时间")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    unit_code: Optional[str] = Field(None, max_length=32)
    unit_name: Optional[str] = Field(None, max_length=64)
    unit_display_name: Optional[str] = Field(None, max_length=64)
    unit_category: Optional[str] = Field(None, max_length=64)
    measurement_system: Optional[str] = Field(None, max_length=64)
    base_unit_id: Optional[int] = None
    unit_factor: Optional[Decimal] = Field(None, ge=0)
    sync_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class UnitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unit_code: str
    unit_name: str
    unit_display_name: Optional[str]
    unit_category: str
    measurement_system: Optional[str]
    base_unit_id: Optional[int]
    unit_factor: Decimal
    sync_time: Optional[datetime]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

