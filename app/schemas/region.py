from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RegionBase(BaseModel):
    region_code: str = Field(..., max_length=64, description="区域编码")
    region_name: str = Field(..., max_length=128, description="区域名称")
    region_type: str = Field(..., max_length=64, description="区域类型")
    parent_id: Optional[int] = Field(None, gt=0, description="上级区域ID")
    level_no: int = Field(1, ge=1, description="层级深度")
    full_name: Optional[str] = Field(None, max_length=512, description="全路径名称")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    region_code: Optional[str] = Field(None, max_length=64)
    region_name: Optional[str] = Field(None, max_length=128)
    region_type: Optional[str] = Field(None, max_length=64)
    parent_id: Optional[int] = Field(None, gt=0)
    level_no: Optional[int] = Field(None, ge=1)
    full_name: Optional[str] = Field(None, max_length=512)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class RegionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_code: str
    region_name: str
    region_type: str
    parent_id: Optional[int]
    level_no: int
    full_name: Optional[str]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

