from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MaterialTypeBase(BaseModel):
    material_type_code: str = Field(..., max_length=64, description="物料类型编码")
    material_type_name: str = Field(..., max_length=128, description="物料类型名称")
    description: Optional[str] = Field(None, max_length=255, description="描述")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class MaterialTypeCreate(MaterialTypeBase):
    pass


class MaterialTypeUpdate(BaseModel):
    material_type_code: Optional[str] = Field(None, max_length=64)
    material_type_name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class MaterialTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_type_code: str
    material_type_name: str
    description: Optional[str]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime
