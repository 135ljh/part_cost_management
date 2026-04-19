from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.bom import Bom
from app.models.bom_item import BomItem
from app.models.part import Part
from app.models.unit import Unit
from app.repositories.bom_repository import BomRepository
from app.schemas.bom import BomCreate, BomItemCreate, BomItemCreateGlobal, BomItemUpdate, BomUpdate


class BomService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BomRepository(db)

    def list_boms(self) -> list[Bom]:
        return self.repo.list_boms()

    def get_bom(self, bom_id: int) -> Bom:
        bom = self.repo.get_bom(bom_id)
        if not bom:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOM不存在")
        return bom

    def _validate_part(self, part_id: int) -> None:
        if not self.db.get(Part, part_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="零件不存在")

    def _validate_item_foreign_keys(
        self,
        bom_id: int,
        child_part_id: int,
        quantity_unit_id: int | None,
        parent_item_id: int | None,
    ) -> None:
        bom = self.repo.get_bom(bom_id)
        if not bom:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="BOM不存在")
        if not self.db.get(Part, child_part_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="子零件不存在")
        if quantity_unit_id is not None and not self.db.get(Unit, quantity_unit_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="数量单位不存在")
        if parent_item_id is not None:
            parent = self.repo.get_item(parent_item_id)
            if parent is None or parent.bom_id != bom_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="父级BOM明细不存在或不属于当前BOM"
                )

    def create_bom(self, payload: BomCreate) -> Bom:
        self._validate_part(payload.part_id)
        existed = self.repo.get_bom_by_code(payload.bom_code)
        if existed is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="BOM编码已存在")

        bom = Bom(
            part_id=payload.part_id,
            bom_code=payload.bom_code,
            bom_name=payload.bom_name,
            version_no=payload.version_no,
            status=payload.status,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            remark=payload.remark,
        )
        try:
            created = self.repo.create_bom(bom)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="创建失败：数据约束冲突")

    def update_bom(self, bom_id: int, payload: BomUpdate) -> Bom:
        bom = self.get_bom(bom_id)
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        new_part_id = update_data.get("part_id", bom.part_id)
        self._validate_part(new_part_id)
        if "bom_code" in update_data:
            existed = self.repo.get_bom_by_code(update_data["bom_code"])
            if existed is not None and existed.id != bom.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="BOM编码已存在")

        for field_name, value in update_data.items():
            setattr(bom, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            refreshed = self.repo.get_bom(bom.id)
            if refreshed is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOM不存在")
            return refreshed
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突")

    def delete_bom(self, bom_id: int) -> None:
        bom = self.get_bom(bom_id)
        try:
            self.repo.delete_bom(bom)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据")

    def list_items(self, bom_id: int) -> list[BomItem]:
        self.get_bom(bom_id)
        return self.repo.list_items(bom_id)

    def list_all_items(self) -> list[BomItem]:
        return self.db.query(BomItem).order_by(BomItem.updated_at.desc(), BomItem.id.desc()).all()

    def get_item_detail(self, item_id: int) -> BomItem:
        item = self.repo.get_item(item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOM明细不存在")
        return item

    def create_item(self, bom_id: int, payload: BomItemCreate) -> BomItem:
        self._validate_item_foreign_keys(
            bom_id=bom_id,
            child_part_id=payload.child_part_id,
            quantity_unit_id=payload.quantity_unit_id,
            parent_item_id=payload.parent_item_id,
        )
        item = BomItem(
            bom_id=bom_id,
            parent_item_id=payload.parent_item_id,
            child_part_id=payload.child_part_id,
            item_name_snapshot=payload.item_name_snapshot,
            item_number_snapshot=payload.item_number_snapshot,
            item_version_snapshot=payload.item_version_snapshot,
            quantity=payload.quantity,
            quantity_unit_id=payload.quantity_unit_id,
            is_outsourced=1 if payload.is_outsourced else 0,
            sort_no=payload.sort_no,
            remark=payload.remark,
        )
        try:
            created = self.repo.create_item(item)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="创建失败：数据约束冲突")

    def create_item_global(self, payload: BomItemCreateGlobal) -> BomItem:
        nested_payload = BomItemCreate(
            parent_item_id=payload.parent_item_id,
            child_part_id=payload.child_part_id,
            item_name_snapshot=payload.item_name_snapshot,
            item_number_snapshot=payload.item_number_snapshot,
            item_version_snapshot=payload.item_version_snapshot,
            quantity=payload.quantity,
            quantity_unit_id=payload.quantity_unit_id,
            is_outsourced=payload.is_outsourced,
            sort_no=payload.sort_no,
            remark=payload.remark,
        )
        return self.create_item(payload.bom_id, nested_payload)

    def update_item(self, bom_id: int, item_id: int, payload: BomItemUpdate) -> BomItem:
        self.get_bom(bom_id)
        item = self.repo.get_item(item_id)
        if item is None or item.bom_id != bom_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOM明细不存在")

        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        new_child_part_id = update_data.get("child_part_id", item.child_part_id)
        new_quantity_unit_id = update_data.get("quantity_unit_id", item.quantity_unit_id)
        new_parent_item_id = update_data.get("parent_item_id", item.parent_item_id)
        self._validate_item_foreign_keys(
            bom_id=bom_id,
            child_part_id=new_child_part_id,
            quantity_unit_id=new_quantity_unit_id,
            parent_item_id=new_parent_item_id,
        )
        if new_parent_item_id == item.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="父级明细不能是自身")

        if "is_outsourced" in update_data:
            update_data["is_outsourced"] = 1 if update_data["is_outsourced"] else 0

        for field_name, value in update_data.items():
            setattr(item, field_name, value)

        try:
            self.db.flush()
            self.db.commit()
            refreshed = self.repo.get_item(item.id)
            if refreshed is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOM明细不存在")
            return refreshed
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突")

    def delete_item(self, bom_id: int, item_id: int) -> None:
        self.get_bom(bom_id)
        item = self.repo.get_item(item_id)
        if item is None or item.bom_id != bom_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOM明细不存在")
        try:
            self.repo.delete_item(item)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据")

    def update_item_global(self, item_id: int, payload: BomItemUpdate) -> BomItem:
        item = self.get_item_detail(item_id)
        return self.update_item(item.bom_id, item_id, payload)

    def delete_item_global(self, item_id: int) -> None:
        item = self.get_item_detail(item_id)
        self.delete_item(item.bom_id, item_id)

    def get_part_bom_detail(self, part_id: int) -> tuple[Part, Bom | None, list[BomItem]]:
        part = self.db.get(Part, part_id)
        if part is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="零件不存在")

        boms = self.repo.list_boms_by_part(part_id)
        if not boms:
            return part, None, []
        # 优先返回最近更新的一版 BOM
        bom = boms[0]
        items = self.repo.list_items(bom.id)
        return part, bom, items
