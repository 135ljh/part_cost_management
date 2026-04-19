from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BomBase(BaseModel):
    part_id: int = Field(..., gt=0, description="父零件ID")
    bom_code: str = Field(..., max_length=64, description="BOM编码")
    bom_name: Optional[str] = Field(None, max_length=128, description="BOM名称")
    version_no: str = Field("V1", max_length=64, description="版本号")
    status: str = Field("DRAFT", max_length=32, description="状态")
    effective_from: Optional[datetime] = Field(None, description="生效开始")
    effective_to: Optional[datetime] = Field(None, description="生效结束")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class BomCreate(BomBase):
    pass


class BomUpdate(BaseModel):
    part_id: Optional[int] = Field(None, gt=0)
    bom_code: Optional[str] = Field(None, max_length=64)
    bom_name: Optional[str] = Field(None, max_length=128)
    version_no: Optional[str] = Field(None, max_length=64)
    status: Optional[str] = Field(None, max_length=32)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    remark: Optional[str] = Field(None, max_length=255)


class BomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    part_id: int
    part_code: Optional[str]
    part_name: Optional[str]
    bom_code: str
    bom_name: Optional[str]
    version_no: str
    status: str
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime


class BomItemBase(BaseModel):
    parent_item_id: Optional[int] = Field(None, gt=0, description="父明细ID")
    child_part_id: int = Field(..., gt=0, description="子零件ID")
    item_name_snapshot: Optional[str] = Field(None, max_length=128, description="名称快照")
    item_number_snapshot: Optional[str] = Field(None, max_length=64, description="编码快照")
    item_version_snapshot: Optional[str] = Field(None, max_length=64, description="版本快照")
    quantity: Decimal = Field(Decimal("1"), description="用量")
    quantity_unit_id: Optional[int] = Field(None, gt=0, description="数量单位ID")
    is_outsourced: bool = Field(False, description="是否外协")
    sort_no: int = Field(1, ge=1, description="排序号")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class BomItemCreate(BomItemBase):
    pass


class BomItemCreateGlobal(BomItemBase):
    bom_id: int = Field(..., gt=0, description="所属BOM")


class BomItemUpdate(BaseModel):
    parent_item_id: Optional[int] = Field(None, gt=0)
    child_part_id: Optional[int] = Field(None, gt=0)
    item_name_snapshot: Optional[str] = Field(None, max_length=128)
    item_number_snapshot: Optional[str] = Field(None, max_length=64)
    item_version_snapshot: Optional[str] = Field(None, max_length=64)
    quantity: Optional[Decimal] = None
    quantity_unit_id: Optional[int] = Field(None, gt=0)
    is_outsourced: Optional[bool] = None
    sort_no: Optional[int] = Field(None, ge=1)
    remark: Optional[str] = Field(None, max_length=255)


class BomItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bom_id: int
    parent_item_id: Optional[int]
    child_part_id: int
    child_part_code: Optional[str]
    child_part_name: Optional[str]
    item_name_snapshot: Optional[str]
    item_number_snapshot: Optional[str]
    item_version_snapshot: Optional[str]
    quantity: Decimal
    quantity_unit_id: Optional[int]
    quantity_unit_name: Optional[str]
    is_outsourced: bool
    sort_no: int
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime


class PartBomDetailRead(BaseModel):
    part_id: int
    part_code: str
    part_name: str
    bom: Optional[BomRead]
    items: list[BomItemRead]
