from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, select

from app.core.database import SessionLocal
from app.models.bom import Bom
from app.models.bom_item import BomItem
from app.models.cost_item import CostItem
from app.models.currency import Currency
from app.models.material import Material
from app.models.material_category import MaterialCategory
from app.models.material_price import MaterialPrice
from app.models.material_type import MaterialType
from app.models.part import Part
from app.models.region import Region
from app.models.unit import Unit


TAG = "DEMO-COST-CTRL"


@dataclass
class OpResult:
    created: int = 0
    reused: int = 0
    updated: int = 0
    check_pass: int = 0
    check_fail: int = 0


def get_or_create(session, model: Any, where_clause, data: dict[str, Any], rs: OpResult):
    row = session.scalars(select(model).where(where_clause)).first()
    if row is not None:
        rs.reused += 1
        return row
    row = model(**data)
    session.add(row)
    session.flush()
    rs.created += 1
    return row


def quant(val: Decimal | int | float | str) -> Decimal:
    return Decimal(str(val)).quantize(Decimal("0.00000001"))


def ensure_base_refs(session, rs: OpResult):
    # Units
    u_pcs = get_or_create(
        session,
        Unit,
        Unit.unit_code == "DEMO-U-PCS",
        {
            "unit_code": "DEMO-U-PCS",
            "unit_name": "件",
            "unit_display_name": "件",
            "unit_category": "COUNT",
            "measurement_system": "METRIC",
            "unit_factor": Decimal("1"),
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )
    u_kg = get_or_create(
        session,
        Unit,
        Unit.unit_code == "DEMO-U-KG",
        {
            "unit_code": "DEMO-U-KG",
            "unit_name": "千克",
            "unit_display_name": "kg",
            "unit_category": "MASS",
            "measurement_system": "METRIC",
            "unit_factor": Decimal("1"),
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )

    # Currency
    cny = get_or_create(
        session,
        Currency,
        Currency.currency_code == "CNY",
        {
            "currency_code": "CNY",
            "currency_name": "人民币",
            "currency_symbol": "¥",
            "precision_scale": 2,
            "is_base_currency": 1,
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )

    # Region
    cn = get_or_create(
        session,
        Region,
        Region.region_code == "CN",
        {
            "region_code": "CN",
            "region_name": "中国",
            "region_type": "COUNTRY",
            "level_no": 1,
            "full_name": "中国",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )
    sh = get_or_create(
        session,
        Region,
        Region.region_code == "CN-SH",
        {
            "region_code": "CN-SH",
            "region_name": "上海",
            "region_type": "PROVINCE",
            "parent_id": cn.id,
            "level_no": 2,
            "full_name": "中国/上海",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )

    # Material category + type
    cat_elec = get_or_create(
        session,
        MaterialCategory,
        MaterialCategory.category_code == "DEMO-CAT-ELEC",
        {
            "category_code": "DEMO-CAT-ELEC",
            "category_name": "电子辅材",
            "category_type": "SUBSTANCE",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )
    mt_asm = get_or_create(
        session,
        MaterialType,
        MaterialType.material_type_code == "DEMO-MT-ASM",
        {
            "material_type_code": "DEMO-MT-ASM",
            "material_type_name": "装配件",
            "description": "总成装配件",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )
    mt_cmp = get_or_create(
        session,
        MaterialType,
        MaterialType.material_type_code == "DEMO-MT-PROC",
        {
            "material_type_code": "DEMO-MT-PROC",
            "material_type_name": "加工件",
            "description": "加工件",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )

    # Materials
    mat_cu = get_or_create(
        session,
        Material,
        Material.material_code == "DEMO-MAT-CU",
        {
            "material_code": "DEMO-MAT-CU",
            "material_name": "电解铜",
            "category_id": cat_elec.id,
            "density": Decimal("8.96"),
            "density_unit_id": u_kg.id,
            "default_quantity_unit_id": u_kg.id,
            "specification": "工业示例铜材",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )
    mat_abs = get_or_create(
        session,
        Material,
        Material.material_code == "DEMO-MAT-ABS",
        {
            "material_code": "DEMO-MAT-ABS",
            "material_name": "ABS树脂",
            "category_id": cat_elec.id,
            "density": Decimal("1.04"),
            "density_unit_id": u_kg.id,
            "default_quantity_unit_id": u_kg.id,
            "specification": "工业示例塑料",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )

    # Material prices
    dt_from = datetime(2026, 1, 1, 0, 0, 0)
    dt_to = datetime(2026, 12, 31, 23, 59, 59)
    get_or_create(
        session,
        MaterialPrice,
        and_(
            MaterialPrice.material_id == mat_cu.id,
            MaterialPrice.region_id == sh.id,
            MaterialPrice.currency_id == cny.id,
            MaterialPrice.supplier_name == "沪上铜材供应",
        ),
        {
            "material_id": mat_cu.id,
            "region_id": sh.id,
            "supplier_name": "沪上铜材供应",
            "currency_id": cny.id,
            "price_unit_id": u_kg.id,
            "unit_price": Decimal("69.5"),
            "effective_from": dt_from,
            "effective_to": dt_to,
            "source_name": "IDME-CTRL-DEMO",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )
    get_or_create(
        session,
        MaterialPrice,
        and_(
            MaterialPrice.material_id == mat_abs.id,
            MaterialPrice.region_id == sh.id,
            MaterialPrice.currency_id == cny.id,
            MaterialPrice.supplier_name == "浦东改性塑料",
        ),
        {
            "material_id": mat_abs.id,
            "region_id": sh.id,
            "supplier_name": "浦东改性塑料",
            "currency_id": cny.id,
            "price_unit_id": u_kg.id,
            "unit_price": Decimal("17.2"),
            "effective_from": dt_from,
            "effective_to": dt_to,
            "source_name": "IDME-CTRL-DEMO",
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )

    return {
        "u_pcs": u_pcs,
        "u_kg": u_kg,
        "cny": cny,
        "sh": sh,
        "mt_asm": mt_asm,
        "mt_cmp": mt_cmp,
        "cat_elec": cat_elec,
        "mat_cu": mat_cu,
        "mat_abs": mat_abs,
    }


def ensure_control_module_bom(session, refs: dict[str, Any], rs: OpResult):
    # Parent assembly
    parent = get_or_create(
        session,
        Part,
        Part.part_code == "DEMO-PART-ASM-CTRL-900",
        {
            "part_code": "DEMO-PART-ASM-CTRL-900",
            "part_name": "伺服控制总成",
            "part_description": "工业设备总成控制模块",
            "part_type": "ASSEMBLY",
            "material_type_id": refs["mt_asm"].id,
            "material_category_id": refs["cat_elec"].id,
            "preferred_material_id": refs["mat_abs"].id,
            "quantity_unit_id": refs["u_pcs"].id,
            "surface_area": Decimal("62.5"),
            "volume": Decimal("28.4"),
            "part_status": "RELEASED",
            "lifecycle_stage": "MASS_PROD",
            "revision_no": "B",
            "version_no": 2,
            "is_active": 1,
            "remark": TAG,
        },
        rs,
    )

    # Components
    children_specs = [
        ("DEMO-PART-CMP-CTRL-310", "控制主板", refs["mat_cu"], Decimal("1")),
        ("DEMO-PART-CMP-CTRL-320", "外壳组件", refs["mat_abs"], Decimal("1")),
        ("DEMO-PART-CMP-CTRL-330", "端子线束", refs["mat_cu"], Decimal("2")),
        ("DEMO-PART-CMP-CTRL-340", "散热风扇组件", refs["mat_abs"], Decimal("1")),
    ]
    child_parts: dict[str, Part] = {}
    for code, name, mat, _qty in children_specs:
        child_parts[code] = get_or_create(
            session,
            Part,
            Part.part_code == code,
            {
                "part_code": code,
                "part_name": name,
                "part_description": f"{name}（总成控制模块子件）",
                "part_type": "COMPONENT",
                "material_type_id": refs["mt_cmp"].id,
                "material_category_id": refs["cat_elec"].id,
                "preferred_material_id": mat.id,
                "quantity_unit_id": refs["u_pcs"].id,
                "surface_area": Decimal("8.0"),
                "volume": Decimal("2.2"),
                "part_status": "RELEASED",
                "lifecycle_stage": "MASS_PROD",
                "revision_no": "A",
                "version_no": 1,
                "is_active": 1,
                "remark": TAG,
            },
            rs,
        )

    bom = get_or_create(
        session,
        Bom,
        Bom.bom_code == "DEMO-BOM-ASM-CTRL-900",
        {
            "part_id": parent.id,
            "bom_code": "DEMO-BOM-ASM-CTRL-900",
            "bom_name": "伺服控制总成-BOM",
            "version_no": "V2",
            "status": "RELEASED",
            "remark": TAG,
        },
        rs,
    )

    for sort_no, (code, _name, _mat, qty) in enumerate(children_specs, start=1):
        cp = child_parts[code]
        get_or_create(
            session,
            BomItem,
            and_(
                BomItem.bom_id == bom.id,
                BomItem.parent_item_id.is_(None),
                BomItem.child_part_id == cp.id,
                BomItem.sort_no == sort_no,
            ),
            {
                "bom_id": bom.id,
                "parent_item_id": None,
                "child_part_id": cp.id,
                "item_name_snapshot": cp.part_name,
                "item_number_snapshot": cp.part_code,
                "item_version_snapshot": cp.revision_no,
                "quantity": qty,
                "quantity_unit_id": refs["u_pcs"].id,
                "is_outsourced": 0,
                "sort_no": sort_no,
                "remark": TAG,
            },
            rs,
        )

    return parent, bom


def upsert_control_cost_item(session, parent: Part, refs: dict[str, Any], rs: OpResult) -> CostItem:
    calc_name = "DEMO-CTRL-2026Q2-成本分析"
    row = session.scalars(
        select(CostItem).where(
            and_(CostItem.part_id == parent.id, CostItem.calculation_name == calc_name)
        )
    ).first()

    # Material
    standard_material_total = quant("3185.40")
    material_scrap_cost = quant("82.30")
    indirect_material_cost = quant("126.00")
    material_inventory_interest = quant("41.00")
    material_cost = quant(
        standard_material_total
        + material_scrap_cost
        + indirect_material_cost
        + material_inventory_interest
    )

    # Manufacturing (I / II)
    direct_equipment_cost = quant("420.60")
    direct_labor_cost = quant("395.20")
    setup_changeover_cost = quant("160.00")
    manufacturing_cost_i = quant(direct_equipment_cost + direct_labor_cost + setup_changeover_cost)

    mold_tooling_cost = quant("228.50")
    remaining_indirect_cost_ii = quant("176.30")
    manufacturing_cost_ii = quant(mold_tooling_cost + remaining_indirect_cost_ii)
    manufacturing_cost = quant(manufacturing_cost_i + manufacturing_cost_ii)

    # Overhead
    special_dev_alloc = quant("96.00")
    special_launch_alloc = quant("65.00")
    packaging_aux_alloc = quant("37.50")
    sales_admin_cost = quant("178.00")
    rnd_cost = quant("148.00")
    business_risk_cost = quant("42.00")
    finished_goods_interest = quant("28.60")
    other_after_prod = quant("35.20")
    direct_mgmt_excl_prod = quant("31.80")
    profit = quant("268.00")
    financing_discount = quant("53.00")
    discount = quant("24.00")
    shipping_cost = quant("86.00")
    tariff = quant("0.00")

    overhead_total = quant(
        special_dev_alloc
        + special_launch_alloc
        + packaging_aux_alloc
        + sales_admin_cost
        + rnd_cost
        + business_risk_cost
        + finished_goods_interest
        + other_after_prod
        + direct_mgmt_excl_prod
        + profit
        + financing_discount
        + discount
        + shipping_cost
        + tariff
    )

    total_cost = quant(material_cost + manufacturing_cost + overhead_total)

    trace = {
        "rule_version": "full_cost_v1",
        "stage": "full_cost",
        "part": {
            "part_id": parent.id,
            "part_code": parent.part_code,
            "part_name": parent.part_name,
        },
        "base_data": {
            "calculation_variables": {
                "region_id": refs["sh"].id,
                "procurement_type": "自制",
                "annual_effective_hours": 5760,
                "net_sale_price": 12800,
                "shifts_per_day": 3,
                "hours_per_shift": 8,
                "days_per_week": 5,
                "extra_shift_per_week": 0,
                "weeks_per_year": 48,
            },
            "production": {
                "qualified_annual_demand": 8200,
                "annual_other_demand": 350,
                "manufacturing_batch_no": "BATCH-CTRL-Q2",
                "part_lifecycle_years": 5,
                "production_start_date": "2026-01-10",
            },
        },
        "material_rows": [
            {
                "name": "控制主板",
                "code": "DEMO-PART-CMP-CTRL-310",
                "quantity": "1.00000000",
                "unit_price": "1280.00000000",
                "input_material_cost": "1280.00000000",
                "standard_material_cost": "1280.00000000",
            },
            {
                "name": "外壳组件",
                "code": "DEMO-PART-CMP-CTRL-320",
                "quantity": "1.00000000",
                "unit_price": "760.00000000",
                "input_material_cost": "760.00000000",
                "standard_material_cost": "760.00000000",
            },
            {
                "name": "端子线束",
                "code": "DEMO-PART-CMP-CTRL-330",
                "quantity": "2.00000000",
                "unit_price": "432.70000000",
                "input_material_cost": "865.40000000",
                "standard_material_cost": "865.40000000",
            },
            {
                "name": "散热风扇组件",
                "code": "DEMO-PART-CMP-CTRL-340",
                "quantity": "1.00000000",
                "unit_price": "280.00000000",
                "input_material_cost": "280.00000000",
                "standard_material_cost": "280.00000000",
            },
        ],
        "material_inputs": {
            "material_scrap_cost": str(material_scrap_cost),
            "indirect_material_cost": str(indirect_material_cost),
            "material_inventory_interest": str(material_inventory_interest),
        },
        "manufacturing": {
            "routes": [
                {
                    "process_name": "控制板贴片与回流",
                    "direct_equipment_cost": str(quant("178.20")),
                    "direct_labor_cost": str(quant("136.00")),
                    "setup_changeover_cost": str(quant("52.00")),
                    "mold_tooling_cost": str(quant("96.50")),
                    "remaining_indirect_cost_ii": str(quant("58.30")),
                    "manufacturing_cost_i": str(quant("366.20")),
                    "manufacturing_cost_ii": str(quant("154.80")),
                    "manufacturing_total": str(quant("521.00")),
                },
                {
                    "process_name": "总成装配与调试",
                    "direct_equipment_cost": str(quant("242.40")),
                    "direct_labor_cost": str(quant("259.20")),
                    "setup_changeover_cost": str(quant("108.00")),
                    "mold_tooling_cost": str(quant("132.00")),
                    "remaining_indirect_cost_ii": str(quant("118.00")),
                    "manufacturing_cost_i": str(quant("609.60")),
                    "manufacturing_cost_ii": str(quant("250.00")),
                    "manufacturing_total": str(quant("859.60")),
                },
            ],
            "totals": {
                "direct_equipment_cost": str(direct_equipment_cost),
                "direct_labor_cost": str(direct_labor_cost),
                "setup_changeover_cost": str(setup_changeover_cost),
                "manufacturing_cost_i": str(manufacturing_cost_i),
                "manufacturing_cost_ii": str(manufacturing_cost_ii),
                "manufacturing_total": str(manufacturing_cost),
            },
        },
        "overhead": {
            "special_dev_alloc": str(special_dev_alloc),
            "special_launch_alloc": str(special_launch_alloc),
            "packaging_aux_alloc": str(packaging_aux_alloc),
            "sales_admin_cost": str(sales_admin_cost),
            "rnd_cost": str(rnd_cost),
            "business_risk_cost": str(business_risk_cost),
            "finished_goods_interest": str(finished_goods_interest),
            "other_after_prod": str(other_after_prod),
            "direct_mgmt_excl_prod": str(direct_mgmt_excl_prod),
            "profit": str(profit),
            "financing_discount": str(financing_discount),
            "discount": str(discount),
            "shipping_cost": str(shipping_cost),
            "tariff": str(tariff),
            "overhead_total": str(overhead_total),
        },
        "components": {
            "standard_material_total": str(standard_material_total),
            "material_scrap_cost": str(material_scrap_cost),
            "indirect_material_cost": str(indirect_material_cost),
            "material_inventory_interest": str(material_inventory_interest),
            "material_cost": str(material_cost),
            "direct_equipment_cost": str(direct_equipment_cost),
            "direct_labor_cost": str(direct_labor_cost),
            "setup_changeover_cost": str(setup_changeover_cost),
            "manufacturing_cost_i": str(manufacturing_cost_i),
            "manufacturing_cost_ii": str(manufacturing_cost_ii),
            "manufacturing_cost": str(manufacturing_cost),
            "special_dev_alloc": str(special_dev_alloc),
            "special_launch_alloc": str(special_launch_alloc),
            "packaging_aux_alloc": str(packaging_aux_alloc),
            "sales_admin_cost": str(sales_admin_cost),
            "rnd_cost": str(rnd_cost),
            "business_risk_cost": str(business_risk_cost),
            "finished_goods_interest": str(finished_goods_interest),
            "other_after_prod": str(other_after_prod),
            "direct_mgmt_excl_prod": str(direct_mgmt_excl_prod),
            "profit": str(profit),
            "financing_discount": str(financing_discount),
            "discount": str(discount),
            "shipping_cost": str(shipping_cost),
            "tariff": str(tariff),
            "overhead_cost": str(overhead_total),
            "total_cost": str(total_cost),
        },
    }

    payload = {
        "calculation_name": calc_name,
        "part_id": parent.id,
        "currency_id": refs["cny"].id,
        "unit_id": refs["u_pcs"].id,
        "material_cost": material_cost,
        "manufacturing_cost": manufacturing_cost,
        "overhead_cost": overhead_total,
        "total_cost": total_cost,
        "rule_version": "full_cost_v1",
        "trace_detail": json.dumps(trace, ensure_ascii=False),
        "remark": TAG,
    }

    if row is None:
        row = CostItem(**payload)
        session.add(row)
        session.flush()
        rs.created += 1
    else:
        for k, v in payload.items():
            setattr(row, k, v)
        session.flush()
        rs.updated += 1
    return row


def validate_cost_item(row: CostItem) -> list[str]:
    errs: list[str] = []
    trace: dict[str, Any] = {}
    try:
        trace = json.loads(row.trace_detail or "{}")
    except Exception as exc:
        errs.append(f"trace_detail 非法JSON: {exc}")
        return errs

    comps = trace.get("components", {}) if isinstance(trace, dict) else {}
    mfg = trace.get("manufacturing", {}).get("totals", {}) if isinstance(trace, dict) else {}
    overhead = trace.get("overhead", {}) if isinstance(trace, dict) else {}

    m1 = quant(comps.get("standard_material_total", "0"))
    m2 = quant(comps.get("material_scrap_cost", "0"))
    m3 = quant(comps.get("indirect_material_cost", "0"))
    m4 = quant(comps.get("material_inventory_interest", "0"))
    expected_material = quant(m1 + m2 + m3 + m4)
    if expected_material != quant(row.material_cost):
        errs.append(
            f"材料成本不一致: expected={expected_material} actual={quant(row.material_cost)}"
        )

    mfg_i = quant(mfg.get("manufacturing_cost_i", comps.get("manufacturing_cost_i", "0")))
    mfg_ii = quant(mfg.get("manufacturing_cost_ii", comps.get("manufacturing_cost_ii", "0")))
    expected_mfg = quant(mfg_i + mfg_ii)
    if expected_mfg != quant(row.manufacturing_cost):
        errs.append(
            f"制造成本不一致: expected={expected_mfg} actual={quant(row.manufacturing_cost)}"
        )

    overhead_total = quant(overhead.get("overhead_total", comps.get("overhead_cost", "0")))
    if overhead_total != quant(row.overhead_cost):
        errs.append(
            f"间接费用不一致: expected={overhead_total} actual={quant(row.overhead_cost)}"
        )

    expected_total = quant(row.material_cost + row.manufacturing_cost + row.overhead_cost)
    if expected_total != quant(row.total_cost):
        errs.append(f"总成本不一致: expected={expected_total} actual={quant(row.total_cost)}")
    return errs


def main():
    rs = OpResult()
    with SessionLocal() as session:
        refs = ensure_base_refs(session, rs)
        parent, _bom = ensure_control_module_bom(session, refs, rs)
        cost_row = upsert_control_cost_item(session, parent, refs, rs)
        session.commit()

        # Validate the newly seeded control module cost
        errs = validate_cost_item(cost_row)
        if errs:
            rs.check_fail += 1
            print("[CHECK][FAIL] 控制模块成本校验失败")
            for e in errs:
                print(" -", e)
        else:
            rs.check_pass += 1
            print("[CHECK][PASS] 控制模块成本校验通过")

        # Validate all full_cost records for quick sanity check
        all_rows = list(
            session.scalars(
                select(CostItem).where(CostItem.rule_version.in_(["full_cost_v1", "material_v1"]))
            ).all()
        )
        fail_rows = 0
        for r in all_rows:
            e = validate_cost_item(r)
            if e:
                fail_rows += 1
                print(f"[CHECK][WARN] cost_item_id={r.id} calculation_name={r.calculation_name}")
                for msg in e:
                    print("   -", msg)
        if fail_rows == 0:
            print("[CHECK][PASS] 所有已检成本记录公式一致")
        else:
            print(f"[CHECK][WARN] 存在 {fail_rows} 条历史记录公式不一致（见上方明细）")

        print("=== CONTROL MODULE DEMO SEEDED ===")
        print(f"created={rs.created}, reused={rs.reused}, updated={rs.updated}")
        print(f"check_pass={rs.check_pass}, check_fail={rs.check_fail}")
        print(f"part={parent.part_code} / cost_item_id={cost_row.id} / total_cost={cost_row.total_cost}")


if __name__ == "__main__":
    main()

