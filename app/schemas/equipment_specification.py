from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EquipmentSpecificationBase(BaseModel):
    equipment_id: int = Field(..., gt=0)
    spec_key: str = Field(..., max_length=64)
    spec_value: str = Field(..., max_length=255)
    spec_unit_id: Optional[int] = Field(None, gt=0)
    sort_no: int = Field(1, ge=1)


class EquipmentSpecificationCreate(EquipmentSpecificationBase):
    pass


class EquipmentSpecificationUpdate(BaseModel):
    equipment_id: Optional[int] = Field(None, gt=0)
    spec_key: Optional[str] = Field(None, max_length=64)
    spec_value: Optional[str] = Field(None, max_length=255)
    spec_unit_id: Optional[int] = Field(None, gt=0)
    sort_no: Optional[int] = Field(None, ge=1)


class EquipmentSpecificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: int
    spec_key: str
    spec_value: str
    spec_unit_id: Optional[int]
    sort_no: int
    created_at: datetime
    updated_at: datetime

