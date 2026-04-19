from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MaterialCategoryBase(BaseModel):
    category_name: str = Field(..., max_length=128, description="物质分类名")
    parent_id: Optional[int] = Field(None, gt=0, description="父物质分类ID")
    category_type: str = Field("SUBSTANCE", max_length=32, description="分类类型")
    is_active: bool = Field(True, description="是否启用")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class MaterialCategoryCreate(MaterialCategoryBase):
    category_code: Optional[str] = Field(None, max_length=64, description="分类编码")


class MaterialCategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, max_length=128)
    parent_id: Optional[int] = Field(None, gt=0)
    category_type: Optional[str] = Field(None, max_length=32)
    is_active: Optional[bool] = None
    remark: Optional[str] = Field(None, max_length=255)


class MaterialCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_code: str
    category_name: str
    category_type: str
    parent_id: Optional[int]
    is_active: bool
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime


class MaterialInCategoryNode(BaseModel):
    id: int
    material_name: str


class MaterialCategoryTreeNode(BaseModel):
    id: int
    category_name: str
    parent_id: Optional[int]
    materials: list[MaterialInCategoryNode]
    children: list["MaterialCategoryTreeNode"]


MaterialCategoryTreeNode.model_rebuild()

