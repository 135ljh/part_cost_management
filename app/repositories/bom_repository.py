from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.bom import Bom
from app.models.bom_item import BomItem


class BomRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_boms(self) -> list[Bom]:
        stmt = (
            select(Bom)
            .options(selectinload(Bom.part))
            .order_by(Bom.updated_at.desc(), Bom.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_boms_by_part(self, part_id: int) -> list[Bom]:
        stmt = (
            select(Bom)
            .options(selectinload(Bom.part))
            .where(Bom.part_id == part_id)
            .order_by(Bom.updated_at.desc(), Bom.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_bom(self, bom_id: int) -> Optional[Bom]:
        stmt = select(Bom).options(selectinload(Bom.part)).where(Bom.id == bom_id)
        return self.db.scalars(stmt).first()

    def get_bom_by_code(self, bom_code: str) -> Optional[Bom]:
        stmt = select(Bom).options(selectinload(Bom.part)).where(Bom.bom_code == bom_code)
        return self.db.scalars(stmt).first()

    def create_bom(self, bom: Bom) -> Bom:
        self.db.add(bom)
        self.db.flush()
        self.db.refresh(bom)
        return bom

    def delete_bom(self, bom: Bom) -> None:
        self.db.delete(bom)
        self.db.flush()

    def list_items(self, bom_id: int) -> list[BomItem]:
        stmt = (
            select(BomItem)
            .options(selectinload(BomItem.child_part), selectinload(BomItem.quantity_unit))
            .where(BomItem.bom_id == bom_id)
            .order_by(BomItem.sort_no.asc(), BomItem.id.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_item(self, item_id: int) -> Optional[BomItem]:
        stmt = (
            select(BomItem)
            .options(selectinload(BomItem.child_part), selectinload(BomItem.quantity_unit))
            .where(BomItem.id == item_id)
        )
        return self.db.scalars(stmt).first()

    def create_item(self, item: BomItem) -> BomItem:
        self.db.add(item)
        self.db.flush()
        self.db.refresh(item)
        return item

    def delete_item(self, item: BomItem) -> None:
        self.db.delete(item)
        self.db.flush()

