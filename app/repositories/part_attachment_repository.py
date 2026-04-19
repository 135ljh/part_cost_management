from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.part_attachment import PartAttachment


class PartAttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_attachments(self) -> list[PartAttachment]:
        stmt = (
            select(PartAttachment)
            .options(selectinload(PartAttachment.part))
            .order_by(PartAttachment.created_at.desc(), PartAttachment.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_by_part(self, part_id: int) -> list[PartAttachment]:
        stmt = (
            select(PartAttachment)
            .options(selectinload(PartAttachment.part))
            .where(PartAttachment.part_id == part_id)
            .order_by(PartAttachment.created_at.desc(), PartAttachment.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, attachment_id: int) -> Optional[PartAttachment]:
        stmt = (
            select(PartAttachment)
            .options(selectinload(PartAttachment.part))
            .where(PartAttachment.id == attachment_id)
        )
        return self.db.scalars(stmt).first()

    def create(self, attachment: PartAttachment) -> PartAttachment:
        self.db.add(attachment)
        self.db.flush()
        self.db.refresh(attachment)
        return attachment

    def delete(self, attachment: PartAttachment) -> None:
        self.db.delete(attachment)
        self.db.flush()

