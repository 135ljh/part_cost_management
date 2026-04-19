from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MaterialBase(BaseModel):
    material_name: str = Field(..., max_length=128, description="物质名称")
    category_id: Optional[int] = Field(None, gt=0, description="物质分类ID")
    density: Optional[Decimal] = Field(None, gt=0, description="密度")
    density_unit_id: Optional[int] = Field(None, gt=0, description="密度单位ID")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class MaterialCreate(MaterialBase):
    material_code: Optional[str] = Field(None, max_length=64, description="物质编码")


class MaterialUpdate(BaseModel):
    material_name: Optional[str] = Field(None, max_length=128)
    category_id: Optional[int] = Field(None, gt=0)
    density: Optional[Decimal] = Field(None, gt=0)
    density_unit_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_code: str
    material_name: str
    category_id: Optional[int]
    density: Optional[Decimal]
    density_unit_id: Optional[int]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

