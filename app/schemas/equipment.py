from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EquipmentBase(BaseModel):
    equipment_name: str = Field(..., max_length=128)
    category_id: Optional[int] = Field(None, gt=0)
    equipment_type: Optional[str] = Field(None, max_length=64)
    manufacturer: Optional[str] = Field(None, max_length=128)
    energy_type: Optional[str] = Field(None, max_length=64)
    specification_text: Optional[str] = Field(None, max_length=255)
    scale_desc: Optional[str] = Field(None, max_length=128)
    is_active: bool = True
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentCreate(EquipmentBase):
    equipment_code: str = Field(..., max_length=64)


class EquipmentUpdate(BaseModel):
    equipment_name: Optional[str] = Field(None, max_length=128)
    category_id: Optional[int] = Field(None, gt=0)
    equipment_type: Optional[str] = Field(None, max_length=64)
    manufacturer: Optional[str] = Field(None, max_length=128)
    energy_type: Optional[str] = Field(None, max_length=64)
    specification_text: Optional[str] = Field(None, max_length=255)
    scale_desc: Optional[str] = Field(None, max_length=128)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class EquipmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_code: str
    equipment_name: str
    category_id: Optional[int]
    equipment_type: Optional[str]
    manufacturer: Optional[str]
    energy_type: Optional[str]
    specification_text: Optional[str]
    scale_desc: Optional[str]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

