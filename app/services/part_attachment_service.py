from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.part import Part
from app.models.part_attachment import PartAttachment
from app.repositories.part_attachment_repository import PartAttachmentRepository
from app.schemas.part_attachment import PartAttachmentCreate, PartAttachmentUpdate


class PartAttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PartAttachmentRepository(db)

    def _validate_part(self, part_id: int) -> None:
        if not self.db.get(Part, part_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="零件不存在")

    def list_attachments(self) -> list[PartAttachment]:
        return self.repo.list_attachments()

    def list_by_part(self, part_id: int) -> list[PartAttachment]:
        self._validate_part(part_id)
        return self.repo.list_by_part(part_id)

    def get_detail(self, attachment_id: int) -> PartAttachment:
        attachment = self.repo.get_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="零件附件不存在")
        return attachment

    def create(self, payload: PartAttachmentCreate) -> PartAttachment:
        self._validate_part(payload.part_id)
        row = PartAttachment(
            part_id=payload.part_id,
            file_name=payload.file_name,
            file_url=payload.file_url,
            file_type=payload.file_type,
            file_size=payload.file_size,
            source_type=payload.source_type,
        )
        try:
            created = self.repo.create(row)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="创建失败：数据约束冲突")

    def update(self, attachment_id: int, payload: PartAttachmentUpdate) -> PartAttachment:
        row = self.get_detail(attachment_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        new_part_id = update_data.get("part_id", row.part_id)
        self._validate_part(new_part_id)

        for field_name, value in update_data.items():
            setattr(row, field_name, value)
        try:
            self.db.flush()
            self.db.commit()
            refreshed = self.repo.get_by_id(row.id)
            if refreshed is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="零件附件不存在")
            return refreshed
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突")

    def delete(self, attachment_id: int) -> None:
        row = self.get_detail(attachment_id)
        try:
            self.repo.delete(row)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据")

