from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cost_item import CostItem


class CostItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_items(self) -> list[CostItem]:
        stmt = (
            select(CostItem)
            .options(selectinload(CostItem.part), selectinload(CostItem.currency), selectinload(CostItem.unit))
            .order_by(CostItem.created_at.desc(), CostItem.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, item_id: int) -> Optional[CostItem]:
        stmt = (
            select(CostItem)
            .options(selectinload(CostItem.part), selectinload(CostItem.currency), selectinload(CostItem.unit))
            .where(CostItem.id == item_id)
        )
        return self.db.scalars(stmt).first()

    def get_latest_by_part(self, part_id: int) -> Optional[CostItem]:
        stmt = (
            select(CostItem)
            .options(selectinload(CostItem.part), selectinload(CostItem.currency), selectinload(CostItem.unit))
            .where(CostItem.part_id == part_id)
            .order_by(CostItem.created_at.desc(), CostItem.id.desc())
        )
        return self.db.scalars(stmt).first()

    def create(self, row: CostItem) -> CostItem:
        self.db.add(row)
        self.db.flush()
        self.db.refresh(row)
        return row

    def delete(self, row: CostItem) -> None:
        self.db.delete(row)
        self.db.flush()

