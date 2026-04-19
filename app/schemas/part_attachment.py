from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PartAttachmentBase(BaseModel):
    part_id: int = Field(..., gt=0, description="零件ID")
    file_name: str = Field(..., max_length=255, description="文件名")
    file_url: str = Field(..., max_length=255, description="文件地址")
    file_type: Optional[str] = Field(None, max_length=64, description="文件类型")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小(字节)")
    source_type: str = Field("UPLOAD", max_length=64, description="来源类型")


class PartAttachmentCreate(PartAttachmentBase):
    pass


class PartAttachmentUpdate(BaseModel):
    part_id: Optional[int] = Field(None, gt=0)
    file_name: Optional[str] = Field(None, max_length=255)
    file_url: Optional[str] = Field(None, max_length=255)
    file_type: Optional[str] = Field(None, max_length=64)
    file_size: Optional[int] = Field(None, ge=0)
    source_type: Optional[str] = Field(None, max_length=64)


class PartAttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    part_id: int
    part_code: Optional[str]
    part_name: Optional[str]
    file_name: str
    file_url: str
    file_type: Optional[str]
    file_size: Optional[int]
    source_type: str
    created_at: datetime

