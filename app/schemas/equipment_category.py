from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EquipmentCategoryBase(BaseModel):
    category_name: str = Field(..., max_length=128)
    parent_id: Optional[int] = Field(None, gt=0)
    is_active: bool = True
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentCategoryCreate(EquipmentCategoryBase):
    category_code: Optional[str] = Field(None, max_length=64)


class EquipmentCategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, max_length=128)
    parent_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_code: str
    category_name: str
    parent_id: Optional[int]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

