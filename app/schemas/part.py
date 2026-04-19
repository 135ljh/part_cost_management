from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PartBase(BaseModel):
    part_code: str = Field(..., max_length=64, description="零件编码")
    part_name: str = Field(..., max_length=128, description="零件名称")
    part_description: Optional[str] = Field(None, max_length=500, description="零件描述")
    part_type: Optional[str] = Field(None, max_length=64, description="零件类型")
    material_category_id: Optional[int] = Field(None, gt=0, description="物料分类ID")
    material_type_id: Optional[int] = Field(None, gt=0, description="物料类型ID")
    preferred_material_id: Optional[int] = Field(None, gt=0, description="默认物料ID")
    quantity_unit_id: Optional[int] = Field(None, gt=0, description="数量单位ID")
    surface_area: Optional[Decimal] = Field(None, description="表面积")
    volume: Optional[Decimal] = Field(None, description="体积")
    cad_file_url: Optional[str] = Field(None, max_length=255, description="CAD 文件地址")
    target_url: Optional[str] = Field(None, max_length=255, description="跳转地址")
    legacy_result: Optional[str] = Field(None, description="旧系统 result 字段兼容")
    legacy_msg: Optional[str] = Field(None, description="旧系统 msg 字段兼容")
    part_status: str = Field("DRAFT", max_length=32, description="零件状态")
    lifecycle_stage: str = Field("DESIGN", max_length=32, description="生命周期阶段")
    revision_no: str = Field("A", max_length=32, description="修订号")
    version_no: int = Field(1, ge=1, description="版本号")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    part_code: Optional[str] = Field(None, max_length=64)
    part_name: Optional[str] = Field(None, max_length=128)
    part_description: Optional[str] = Field(None, max_length=500)
    part_type: Optional[str] = Field(None, max_length=64)
    material_category_id: Optional[int] = Field(None, gt=0)
    material_type_id: Optional[int] = Field(None, gt=0)
    preferred_material_id: Optional[int] = Field(None, gt=0)
    quantity_unit_id: Optional[int] = Field(None, gt=0)
    surface_area: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    cad_file_url: Optional[str] = Field(None, max_length=255)
    target_url: Optional[str] = Field(None, max_length=255)
    legacy_result: Optional[str] = None
    legacy_msg: Optional[str] = None
    part_status: Optional[str] = Field(None, max_length=32)
    lifecycle_stage: Optional[str] = Field(None, max_length=32)
    revision_no: Optional[str] = Field(None, max_length=32)
    version_no: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class PartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    part_code: str
    part_name: str
    part_description: Optional[str]
    part_type: Optional[str]
    material_category_id: Optional[int]
    material_category_name: Optional[str]
    material_type_id: Optional[int]
    material_type_name: Optional[str]
    preferred_material_id: Optional[int]
    preferred_material_name: Optional[str]
    quantity_unit_id: Optional[int]
    quantity_unit_name: Optional[str]
    surface_area: Optional[Decimal]
    volume: Optional[Decimal]
    cad_file_url: Optional[str]
    target_url: Optional[str]
    legacy_result: Optional[str]
    legacy_msg: Optional[str]
    part_status: str
    lifecycle_stage: str
    revision_no: str
    version_no: int
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime
