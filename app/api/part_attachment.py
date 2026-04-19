from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.part_attachment import (
    PartAttachmentCreate,
    PartAttachmentRead,
    PartAttachmentUpdate,
)
from app.services.part_attachment_service import PartAttachmentService


router = APIRouter(prefix="/part-attachments", tags=["零件附件"])


@router.get("", response_model=list[PartAttachmentRead], summary="零件附件列表")
def list_part_attachments(db: Session = Depends(get_db)) -> list[PartAttachmentRead]:
    return PartAttachmentService(db).list_attachments()


@router.get("/part/{part_id}", response_model=list[PartAttachmentRead], summary="按零件查看附件")
def list_part_attachments_by_part(part_id: int, db: Session = Depends(get_db)) -> list[PartAttachmentRead]:
    return PartAttachmentService(db).list_by_part(part_id)


@router.get("/{attachment_id}", response_model=PartAttachmentRead, summary="附件详情")
def get_part_attachment(attachment_id: int, db: Session = Depends(get_db)) -> PartAttachmentRead:
    return PartAttachmentService(db).get_detail(attachment_id)


@router.post("", response_model=PartAttachmentRead, status_code=status.HTTP_201_CREATED, summary="新建附件")
def create_part_attachment(
    payload: PartAttachmentCreate, db: Session = Depends(get_db)
) -> PartAttachmentRead:
    return PartAttachmentService(db).create(payload)


@router.put("/{attachment_id}", response_model=PartAttachmentRead, summary="更新附件")
def update_part_attachment(
    attachment_id: int, payload: PartAttachmentUpdate, db: Session = Depends(get_db)
) -> PartAttachmentRead:
    return PartAttachmentService(db).update(attachment_id, payload)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除附件")
def delete_part_attachment(attachment_id: int, db: Session = Depends(get_db)) -> Response:
    PartAttachmentService(db).delete(attachment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

