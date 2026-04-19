import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.bom import Bom
from app.models.bom_item import BomItem
from app.models.cost_item import CostItem
from app.models.currency import Currency
from app.models.material_price import MaterialPrice
from app.models.part import Part
from app.models.unit import Unit
from app.repositories.cost_item_repository import CostItemRepository
from app.schemas.cost_item import CostCalcRequest, CostItemCreate, CostItemUpdate


def _q(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)


class CostItemService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CostItemRepository(db)

    def _validate_fk(self, part_id: int, currency_id: int, unit_id: int | None) -> None:
        if not self.db.get(Part, part_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="零件不存在")
        if not self.db.get(Currency, currency_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="币种不存在")
        if unit_id is not None and not self.db.get(Unit, unit_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="数量单位不存在")

    def list_items(self) -> list[CostItem]:
        return self.repo.list_items()

    def get_detail(self, item_id: int) -> CostItem:
        row = self.repo.get_by_id(item_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成本记录不存在")
        return row

    def get_latest_by_part(self, part_id: int) -> CostItem:
        row = self.repo.get_latest_by_part(part_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该零件暂无成本记录")
        return row

    def create(self, payload: CostItemCreate) -> CostItem:
        self._validate_fk(payload.part_id, payload.currency_id, payload.unit_id)
        row = CostItem(**payload.model_dump())
        try:
            created = self.repo.create(row)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="创建失败：数据约束冲突")

    def update(self, item_id: int, payload: CostItemUpdate) -> CostItem:
        row = self.get_detail(item_id)
        data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        part_id = data.get("part_id", row.part_id)
        currency_id = data.get("currency_id", row.currency_id)
        unit_id = data.get("unit_id", row.unit_id)
        self._validate_fk(part_id, currency_id, unit_id)

        for k, v in data.items():
            setattr(row, k, v)
        try:
            self.db.flush()
            self.db.commit()
            return self.get_detail(row.id)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突")

    def delete(self, item_id: int) -> None:
        row = self.get_detail(item_id)
        try:
            self.repo.delete(row)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="删除失败：存在关联数据")

    def _resolve_defaults(self, req: CostCalcRequest, part: Part) -> tuple[int, int | None]:
        currency_id = req.currency_id
        if currency_id is None:
            cny = self.db.scalars(select(Currency).where(Currency.currency_code == "CNY")).first()
            currency_id = cny.id if cny else None
        if currency_id is None:
            any_ccy = self.db.scalars(select(Currency).order_by(Currency.id.asc())).first()
            if any_ccy is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="系统未配置币种")
            currency_id = any_ccy.id
        unit_id = req.unit_id if req.unit_id is not None else part.quantity_unit_id
        return currency_id, unit_id

    def _material_fallback_from_bom(self, part: Part) -> tuple[Decimal, list[dict[str, Any]]]:
        direct_material = Decimal("0")
        material_rows: list[dict[str, Any]] = []

        bom = self.db.scalars(
            select(Bom).where(Bom.part_id == part.id).order_by(Bom.updated_at.desc(), Bom.id.desc())
        ).first()
        items: list[BomItem] = []
        if bom is not None:
            items = list(
                self.db.scalars(
                    select(BomItem).where(BomItem.bom_id == bom.id).order_by(BomItem.sort_no.asc(), BomItem.id.asc())
                ).all()
            )

        if items:
            for bi in items:
                child = self.db.get(Part, bi.child_part_id)
                if child is None:
                    continue
                mp = self.db.scalars(
                    select(MaterialPrice)
                    .where(MaterialPrice.material_id == child.preferred_material_id)
                    .order_by(MaterialPrice.updated_at.desc(), MaterialPrice.id.desc())
                ).first()
                unit_price = Decimal(mp.unit_price) if mp and mp.unit_price is not None else Decimal("1")
                qty = Decimal(bi.quantity or 0)
                line = qty * unit_price
                direct_material += line
                material_rows.append(
                    {
                        "name": child.part_name,
                        "code": child.part_code,
                        "quantity": str(_q(qty)),
                        "unit_price": str(_q(unit_price)),
                        "input_material_cost": str(_q(line)),
                        "standard_material_cost": str(_q(line)),
                    }
                )
        else:
            mp = self.db.scalars(
                select(MaterialPrice)
                .where(MaterialPrice.material_id == part.preferred_material_id)
                .order_by(MaterialPrice.updated_at.desc(), MaterialPrice.id.desc())
            ).first()
            unit_price = Decimal(mp.unit_price) if mp and mp.unit_price is not None else Decimal("10")
            direct_material = unit_price
            material_rows.append(
                {
                    "name": part.part_name,
                    "code": part.part_code,
                    "quantity": "1.00000000",
                    "unit_price": str(_q(unit_price)),
                    "input_material_cost": str(_q(unit_price)),
                    "standard_material_cost": str(_q(unit_price)),
                }
            )

        return _q(direct_material), material_rows

    def calculate_for_part(self, part_id: int, req: CostCalcRequest) -> CostItem:
        part = self.db.get(Part, part_id)
        if part is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="零件不存在")

        currency_id, unit_id = self._resolve_defaults(req, part)
        self._validate_fk(part.id, currency_id, unit_id)

        # ===== 材料成本计算（对齐 JSON）=====
        # 有效配重 = 理论投料重量 * (1 + 投料损失/100)
        # 废料重量 = 有效配重 - 净重
        # 处理废料费用 = 废料重量 * (废料支出单价 - 废料收入单价)
        # 标准材料成本总计 = (材料单位基价 * 有效配重) + 处理废料费用
        # 材料成本 = 标准材料成本总计 + 材料报废成本 + 材料间接费用 + 材料库存利息

        material_rows: list[dict[str, Any]] = []
        if req.theoretical_feed_weight is not None and req.material_unit_price is not None:
            feed_weight = Decimal(req.theoretical_feed_weight)
            loss_rate = Decimal(req.feed_loss_rate)
            effective_weight = feed_weight * (Decimal("1") + loss_rate / Decimal("100"))
            net_weight = Decimal(req.net_weight) if req.net_weight is not None else effective_weight
            scrap_weight = max(effective_weight - net_weight, Decimal("0"))
            scrap_rate = (scrap_weight / effective_weight * Decimal("100")) if effective_weight > 0 else Decimal("0")

            unit_price = Decimal(req.material_unit_price)
            waste_income_price = Decimal(req.waste_income_price)
            waste_expense_price = Decimal(req.waste_expense_price)

            input_material_cost = unit_price * effective_weight
            scrap_process_cost = scrap_weight * (waste_expense_price - waste_income_price)
            standard_material_total = input_material_cost + scrap_process_cost

            material_rows.append(
                {
                    "name": part.part_name,
                    "code": part.part_code,
                    "theoretical_feed_weight": str(_q(feed_weight)),
                    "feed_loss_rate": str(_q(loss_rate)),
                    "effective_weight": str(_q(effective_weight)),
                    "net_weight": str(_q(net_weight)),
                    "material_unit_price": str(_q(unit_price)),
                    "input_material_cost": str(_q(input_material_cost)),
                    "scrap_weight": str(_q(scrap_weight)),
                    "scrap_rate": str(_q(scrap_rate)),
                    "waste_income_price": str(_q(waste_income_price)),
                    "waste_expense_price": str(_q(waste_expense_price)),
                    "scrap_process_cost": str(_q(scrap_process_cost)),
                    "standard_material_cost": str(_q(standard_material_total)),
                }
            )
            direct_material_total = _q(standard_material_total)
        else:
            direct_material_total, material_rows = self._material_fallback_from_bom(part)

        material_scrap_cost = _q(Decimal(req.material_scrap_cost))
        indirect_material_cost = _q(Decimal(req.indirect_material_cost))
        material_inventory_interest = _q(Decimal(req.material_inventory_interest))
        material_cost = _q(
            direct_material_total + material_scrap_cost + indirect_material_cost + material_inventory_interest
        )

        # 当前阶段仅开发材料成本，其余先置零
        manufacturing_cost = Decimal("0")
        overhead_cost = Decimal("0")
        total_cost = material_cost

        trace = {
            "rule_version": "material_v1",
            "stage": "material_only",
            "part": {"part_id": part.id, "part_code": part.part_code, "part_name": part.part_name},
            "formula": {
                "effective_weight": "theoretical_feed_weight * (1 + feed_loss_rate/100)",
                "scrap_weight": "effective_weight - net_weight",
                "scrap_process_cost": "scrap_weight * (waste_expense_price - waste_income_price)",
                "standard_material_total": "(material_unit_price * effective_weight) + scrap_process_cost",
                "material_cost": "standard_material_total + material_scrap_cost + indirect_material_cost + material_inventory_interest",
                "manufacturing_cost": "0 (not implemented yet)",
                "overhead_cost": "0 (not implemented yet)",
                "total_cost": "material_cost",
            },
            "components": {
                "standard_material_total": str(_q(direct_material_total)),
                "material_scrap_cost": str(material_scrap_cost),
                "indirect_material_cost": str(indirect_material_cost),
                "material_inventory_interest": str(material_inventory_interest),
                "material_cost": str(_q(material_cost)),
                "manufacturing_cost": "0",
                "overhead_cost": "0",
                "total_cost": str(_q(total_cost)),
            },
            "material_rows": material_rows,
        }

        row = CostItem(
            calculation_name=req.calculation_name or f"{part.part_code}-材料成本计算",
            part_id=part.id,
            currency_id=currency_id,
            unit_id=unit_id,
            material_cost=_q(material_cost),
            manufacturing_cost=manufacturing_cost,
            overhead_cost=overhead_cost,
            total_cost=_q(total_cost),
            rule_version="material_v1",
            trace_detail=json.dumps(trace, ensure_ascii=False),
            remark=req.remark or "材料成本阶段自动计算",
        )
        try:
            created = self.repo.create(row)
            self.db.commit()
            return created
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="成本计算写入失败：约束冲突")
