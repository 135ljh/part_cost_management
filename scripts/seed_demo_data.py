from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, select

from app.core.database import SessionLocal
from app.models.bom import Bom
from app.models.bom_item import BomItem
from app.models.currency import Currency
from app.models.currency_exchange_rate import CurrencyExchangeRate
from app.models.equipment import Equipment
from app.models.equipment_category import EquipmentCategory
from app.models.equipment_cost_profile import EquipmentCostProfile
from app.models.equipment_rate import EquipmentRate
from app.models.equipment_specification import EquipmentSpecification
from app.models.material import Material
from app.models.material_category import MaterialCategory
from app.models.material_price import MaterialPrice
from app.models.material_type import MaterialType
from app.models.part import Part
from app.models.part_attachment import PartAttachment
from app.models.region import Region
from app.models.region_cost_profile import RegionCostProfile
from app.models.unit import Unit

TAG = "DEMO-SEED"


@dataclass
class SeedResult:
    created: int = 0
    reused: int = 0


def get_or_create(session, model: Any, where_clause, data: dict[str, Any], result: SeedResult):
    row = session.scalars(select(model).where(where_clause)).first()
    if row is not None:
        result.reused += 1
        return row
    row = model(**data)
    session.add(row)
    session.flush()
    result.created += 1
    return row


def seed_base(session, result: SeedResult):
    units = {}
    for code, name, cat in [
        ("DEMO-U-PCS", "件", "COUNT"),
        ("DEMO-U-KG", "千克", "MASS"),
        ("DEMO-U-MM", "毫米", "LENGTH"),
        ("DEMO-U-H", "小时", "TIME"),
    ]:
        units[code] = get_or_create(
            session,
            Unit,
            Unit.unit_code == code,
            {
                "unit_code": code,
                "unit_name": name,
                "unit_display_name": name,
                "unit_category": cat,
                "measurement_system": "METRIC",
                "unit_factor": Decimal("1"),
                "is_active": 1,
                "remark": TAG,
            },
            result,
        )

    currencies = {}
    for code, name, sym, base in [("CNY", "人民币", "¥", 1), ("USD", "美元", "$", 0), ("EUR", "欧元", "€", 0)]:
        currencies[code] = get_or_create(
            session,
            Currency,
            Currency.currency_code == code,
            {
                "currency_code": code,
                "currency_name": name,
                "currency_symbol": sym,
                "precision_scale": 2,
                "is_base_currency": base,
                "is_active": 1,
                "remark": TAG,
            },
            result,
        )

    dt = datetime(2026, 1, 1, 0, 0, 0)
    for f, t, rate in [("CNY", "USD", "0.138"), ("USD", "CNY", "7.246"), ("CNY", "EUR", "0.128"), ("EUR", "CNY", "7.810")]:
        get_or_create(
            session,
            CurrencyExchangeRate,
            and_(
                CurrencyExchangeRate.from_currency_id == currencies[f].id,
                CurrencyExchangeRate.to_currency_id == currencies[t].id,
                CurrencyExchangeRate.rate_type == "FIXED",
                CurrencyExchangeRate.effective_date == dt,
            ),
            {
                "from_currency_id": currencies[f].id,
                "to_currency_id": currencies[t].id,
                "rate_type": "FIXED",
                "exchange_rate": Decimal(rate),
                "effective_date": dt,
                "source_name": "IDME-DEMO",
                "is_active": 1,
                "remark": TAG,
            },
            result,
        )

    regions = {}
    regions["CN"] = get_or_create(session, Region, Region.region_code == "CN", {"region_code": "CN", "region_name": "中国", "region_type": "COUNTRY", "level_no": 1, "full_name": "中国", "is_active": 1, "remark": TAG}, result)
    regions["CN-SH"] = get_or_create(session, Region, Region.region_code == "CN-SH", {"region_code": "CN-SH", "region_name": "上海", "region_type": "PROVINCE", "parent_id": regions["CN"].id, "level_no": 2, "full_name": "中国/上海", "is_active": 1, "remark": TAG}, result)
    regions["US"] = get_or_create(session, Region, Region.region_code == "US", {"region_code": "US", "region_name": "美国", "region_type": "COUNTRY", "level_no": 1, "full_name": "美国", "is_active": 1, "remark": TAG}, result)

    for code, name, rkey, ccy, op, eg in [
        ("DEMO-RCP-SH-A", "上海工厂A", "CN-SH", "CNY", "68", "96"),
        ("DEMO-RCP-US-A", "加州工厂A", "US", "USD", "22", "34"),
    ]:
        get_or_create(
            session,
            RegionCostProfile,
            RegionCostProfile.profile_code == code,
            {
                "profile_code": code,
                "profile_name": name,
                "region_id": regions[rkey].id,
                "supplier_name": name,
                "supplier_code": code,
                "currency_id": currencies[ccy].id,
                "operating_worker_rate": Decimal(op),
                "skilled_worker_rate": Decimal(op) * Decimal("1.15"),
                "transfer_technician_rate": Decimal(op) * Decimal("1.20"),
                "production_leader_rate": Decimal(op) * Decimal("1.25"),
                "inspector_rate": Decimal(op) * Decimal("1.10"),
                "engineer_rate": Decimal(eg),
                "mold_fitter_rate": Decimal(op) * Decimal("1.18"),
                "cost_interest_rate": Decimal("0.055"),
                "benefits_one_shift": Decimal("18"),
                "benefits_two_shift": Decimal("28"),
                "benefits_three_shift": Decimal("36"),
                "factory_rent": Decimal("85"),
                "office_fee": Decimal("20"),
                "electricity_fee": Decimal("0.92"),
                "water_fee": Decimal("0.18"),
                "gas_fee": Decimal("0.42"),
                "is_active": 1,
                "remark": TAG,
            },
            result,
        )
    return units, currencies, regions


def seed_materials(session, units: dict[str, Unit], currencies: dict[str, Currency], regions: dict[str, Region], result: SeedResult):
    cats = {}
    for code, name in [("DEMO-CAT-METAL", "金属材料"), ("DEMO-CAT-POLYMER", "高分子材料"), ("DEMO-CAT-ELEC", "电子辅材")]:
        cats[code] = get_or_create(
            session,
            MaterialCategory,
            MaterialCategory.category_code == code,
            {"category_code": code, "category_name": name, "category_type": "SUBSTANCE", "is_active": 1, "remark": TAG},
            result,
        )

    mats = {}
    specs = [
        ("DEMO-MAT-AL6061", "铝合金6061", "DEMO-CAT-METAL", "2.7"),
        ("DEMO-MAT-S45C", "中碳钢S45C", "DEMO-CAT-METAL", "7.85"),
        ("DEMO-MAT-ABS", "ABS树脂", "DEMO-CAT-POLYMER", "1.04"),
        ("DEMO-MAT-PC", "PC树脂", "DEMO-CAT-POLYMER", "1.20"),
        ("DEMO-MAT-CU", "电解铜", "DEMO-CAT-ELEC", "8.96"),
    ]
    for code, name, cat, density in specs:
        mats[code] = get_or_create(
            session,
            Material,
            Material.material_code == code,
            {
                "material_code": code,
                "material_name": name,
                "category_id": cats[cat].id,
                "density": Decimal(density),
                "density_unit_id": units["DEMO-U-KG"].id,
                "default_quantity_unit_id": units["DEMO-U-KG"].id,
                "specification": "工业示例物料",
                "is_active": 1,
                "remark": TAG,
            },
            result,
        )

    dt_from = datetime(2026, 1, 1, 0, 0, 0)
    dt_to = datetime(2026, 12, 31, 23, 59, 59)
    for mcode, rcode, supplier, ccy, price in [
        ("DEMO-MAT-AL6061", "CN-SH", "沪东材料供应", "CNY", "23.5"),
        ("DEMO-MAT-S45C", "CN-SH", "沪钢联", "CNY", "12.8"),
        ("DEMO-MAT-ABS", "CN-SH", "浦江聚合物", "CNY", "16.2"),
        ("DEMO-MAT-PC", "US", "Polymer West", "USD", "4.9"),
        ("DEMO-MAT-CU", "US", "West Copper Inc.", "USD", "9.7"),
    ]:
        get_or_create(
            session,
            MaterialPrice,
            and_(MaterialPrice.material_id == mats[mcode].id, MaterialPrice.region_id == regions[rcode].id, MaterialPrice.supplier_name == supplier, MaterialPrice.currency_id == currencies[ccy].id),
            {
                "material_id": mats[mcode].id,
                "region_id": regions[rcode].id,
                "supplier_name": supplier,
                "currency_id": currencies[ccy].id,
                "price_unit_id": units["DEMO-U-KG"].id,
                "unit_price": Decimal(price),
                "effective_from": dt_from,
                "effective_to": dt_to,
                "source_name": "IDME-DEMO",
                "is_active": 1,
                "remark": TAG,
            },
            result,
        )
    return cats, mats


def seed_equipment(session, currencies: dict[str, Currency], units: dict[str, Unit], result: SeedResult):
    ecats = {}
    for code, name in [("DEMO-ECAT-INJ", "注塑设备"), ("DEMO-ECAT-CNC", "机加设备"), ("DEMO-ECAT-ASM", "装配设备")]:
        ecats[code] = get_or_create(session, EquipmentCategory, EquipmentCategory.category_code == code, {"category_code": code, "category_name": name, "is_active": 1, "remark": TAG}, result)

    eqs = {}
    for code, name, c, etype, mfr in [
        ("DEMO-EQ-INJ-160T", "注塑机160T", "DEMO-ECAT-INJ", "INJECTION", "Haitian"),
        ("DEMO-EQ-CNC-5AX", "五轴加工中心", "DEMO-ECAT-CNC", "CNC", "DMG MORI"),
        ("DEMO-EQ-ASM-L1", "自动装配线L1", "DEMO-ECAT-ASM", "ASSEMBLY", "Bosch"),
    ]:
        eqs[code] = get_or_create(
            session, Equipment, Equipment.equipment_code == code,
            {"equipment_code": code, "equipment_name": name, "category_id": ecats[c].id, "equipment_type": etype, "manufacturer": mfr, "energy_type": "ELECTRIC", "specification_text": "工业示例设备", "scale_desc": "DEMO", "is_active": 1, "remark": TAG}, result
        )

    for eq_code, key, val in [("DEMO-EQ-INJ-160T", "CLAMP_FORCE", "160"), ("DEMO-EQ-CNC-5AX", "MAX_RPM", "18000"), ("DEMO-EQ-ASM-L1", "LINE_SPEED", "18")]:
        get_or_create(
            session, EquipmentSpecification,
            and_(EquipmentSpecification.equipment_id == eqs[eq_code].id, EquipmentSpecification.spec_key == key),
            {"equipment_id": eqs[eq_code].id, "spec_key": key, "spec_value": val, "spec_unit_id": units["DEMO-U-MM"].id if key == "CLAMP_FORCE" else None, "sort_no": 1},
            result,
        )

    for code, eq, cat, rate in [("DEMO-ER-160T", "DEMO-EQ-INJ-160T", "DEMO-ECAT-INJ", "1.85"), ("DEMO-ER-CNC5", "DEMO-EQ-CNC-5AX", "DEMO-ECAT-CNC", "3.10"), ("DEMO-ER-ASM1", "DEMO-EQ-ASM-L1", "DEMO-ECAT-ASM", "1.20")]:
        get_or_create(
            session, EquipmentRate, EquipmentRate.rate_code == code,
            {"rate_code": code, "equipment_id": eqs[eq].id, "equipment_category_id": ecats[cat].id, "description": "工业示例费率", "equipment_type": eqs[eq].equipment_type, "manpower": 1, "labor_group": "DEMO-LABOR", "direct_labor": Decimal("0.8"), "direct_fringe": Decimal("0.2"), "indirect_labor": Decimal("0.3"), "indirect_fringe": Decimal("0.1"), "total_labor": Decimal("1.4"), "depreciation": Decimal("0.5"), "insurance": Decimal("0.08"), "floor_space": Decimal("0.06"), "mro_labor": Decimal("0.12"), "utilities": Decimal("0.2"), "indirect_materials": Decimal("0.05"), "other_burden": Decimal("0.1"), "total_burden": Decimal("1.11"), "total_minute_rate": Decimal(rate), "investment": Decimal("250000"), "currency_id": currencies["CNY"].id, "is_active": 1, "remark": TAG},
            result,
        )

    for eq_code, profile, hr in [("DEMO-EQ-INJ-160T", "DEMO-ECP-160T", "42"), ("DEMO-EQ-CNC-5AX", "DEMO-ECP-CNC5", "88"), ("DEMO-EQ-ASM-L1", "DEMO-ECP-ASM1", "35")]:
        get_or_create(
            session, EquipmentCostProfile, and_(EquipmentCostProfile.equipment_id == eqs[eq_code].id, EquipmentCostProfile.profile_name == profile),
            {"equipment_id": eqs[eq_code].id, "profile_name": profile, "equipment_number_snapshot": eqs[eq_code].equipment_code, "manufacturer_snapshot": eqs[eq_code].manufacturer, "technical_reliability": Decimal("0.96"), "currency_id": currencies["CNY"].id, "acquisition_value": Decimal("450000"), "number_of_equipment": Decimal("1"), "annual_production_hours": Decimal("5800"), "equipment_efficiency": Decimal("0.88"), "installation_expenses": Decimal("18000"), "foundation_expenses": Decimal("9000"), "other_expenses": Decimal("5000"), "residual_value": Decimal("30000"), "equipment_lifespan_years": Decimal("8"), "estimated_depreciation": Decimal("52500"), "interest_rate": Decimal("0.055"), "total_area_required": Decimal("22"), "production_site_cost": Decimal("120"), "rated_power": Decimal("45"), "electricity_usage_ratio": Decimal("0.72"), "power_cost_electricity": Decimal("0.92"), "maintenance_cost": Decimal("14500"), "auxiliary_material_cost": Decimal("4200"), "total_fixed_cost": Decimal("68000"), "total_variable_cost": Decimal("26000"), "cost_per_unit_time": Decimal("0.7"), "hourly_rate": Decimal(hr), "equipment_cost": Decimal("360000"), "investment": Decimal("450000"), "asset_status": "RUNNING", "is_active": 1, "remark": TAG},
            result,
        )


def seed_parts_bom_attachment(session, units: dict[str, Unit], cats: dict[str, MaterialCategory], mats: dict[str, Material], result: SeedResult):
    mtypes = {}
    for code, name in [("DEMO-MT-RAW", "原材料件"), ("DEMO-MT-STD", "标准件"), ("DEMO-MT-PROC", "加工件"), ("DEMO-MT-ASM", "装配件")]:
        mtypes[code] = get_or_create(session, MaterialType, MaterialType.material_type_code == code, {"material_type_code": code, "material_type_name": name, "description": "工业示例物料类型", "is_active": 1, "remark": TAG}, result)

    parts = {}
    specs = [
        ("DEMO-PART-ASM-100", "总成-驱动模块", "ASSEMBLY", "DEMO-MT-ASM", "DEMO-CAT-METAL", "DEMO-MAT-AL6061"),
        ("DEMO-PART-ASM-200", "总成-控制模块", "ASSEMBLY", "DEMO-MT-ASM", "DEMO-CAT-ELEC", "DEMO-MAT-CU"),
        ("DEMO-PART-CMP-110", "轴承座", "COMPONENT", "DEMO-MT-PROC", "DEMO-CAT-METAL", "DEMO-MAT-S45C"),
        ("DEMO-PART-CMP-120", "传动轴", "COMPONENT", "DEMO-MT-PROC", "DEMO-CAT-METAL", "DEMO-MAT-S45C"),
        ("DEMO-PART-CMP-210", "控制板支架", "COMPONENT", "DEMO-MT-PROC", "DEMO-CAT-METAL", "DEMO-MAT-AL6061"),
        ("DEMO-PART-CMP-220", "端子排", "COMPONENT", "DEMO-MT-STD", "DEMO-CAT-ELEC", "DEMO-MAT-CU"),
    ]
    for code, name, ptype, mt, cat, mat in specs:
        parts[code] = get_or_create(
            session, Part, Part.part_code == code,
            {"part_code": code, "part_name": name, "part_description": f"{name}（工业演示样例）", "part_type": ptype, "material_type_id": mtypes[mt].id, "material_category_id": cats[cat].id, "preferred_material_id": mats[mat].id, "quantity_unit_id": units["DEMO-U-PCS"].id, "surface_area": Decimal("12.5"), "volume": Decimal("5.8"), "cad_file_url": f"https://example.com/cad/{code}.step", "target_url": f"https://example.com/parts/{code}", "legacy_result": "OK", "legacy_msg": "seeded", "part_status": "RELEASED", "lifecycle_stage": "MASS_PROD", "revision_no": "A", "version_no": 1, "is_active": 1, "remark": TAG},
            result,
        )

    bom = get_or_create(session, Bom, Bom.bom_code == "DEMO-BOM-DEMO-PART-ASM-100", {"part_id": parts["DEMO-PART-ASM-100"].id, "bom_code": "DEMO-BOM-DEMO-PART-ASM-100", "bom_name": "驱动模块-BOM", "version_no": "V1", "status": "RELEASED", "remark": TAG}, result)
    root = get_or_create(session, BomItem, and_(BomItem.bom_id == bom.id, BomItem.child_part_id == parts["DEMO-PART-CMP-110"].id, BomItem.sort_no == 1, BomItem.parent_item_id.is_(None)),
        {"bom_id": bom.id, "parent_item_id": None, "child_part_id": parts["DEMO-PART-CMP-110"].id, "item_name_snapshot": parts["DEMO-PART-CMP-110"].part_name, "item_number_snapshot": parts["DEMO-PART-CMP-110"].part_code, "item_version_snapshot": "A", "quantity": Decimal("2"), "quantity_unit_id": units["DEMO-U-PCS"].id, "is_outsourced": 0, "sort_no": 1, "remark": TAG}, result)
    get_or_create(session, BomItem, and_(BomItem.bom_id == bom.id, BomItem.child_part_id == parts["DEMO-PART-CMP-120"].id, BomItem.sort_no == 2, BomItem.parent_item_id.is_(None)),
        {"bom_id": bom.id, "parent_item_id": None, "child_part_id": parts["DEMO-PART-CMP-120"].id, "item_name_snapshot": parts["DEMO-PART-CMP-120"].part_name, "item_number_snapshot": parts["DEMO-PART-CMP-120"].part_code, "item_version_snapshot": "A", "quantity": Decimal("1"), "quantity_unit_id": units["DEMO-U-PCS"].id, "is_outsourced": 0, "sort_no": 2, "remark": TAG}, result)
    get_or_create(session, BomItem, and_(BomItem.bom_id == bom.id, BomItem.child_part_id == parts["DEMO-PART-CMP-210"].id, BomItem.sort_no == 3, BomItem.parent_item_id == root.id),
        {"bom_id": bom.id, "parent_item_id": root.id, "child_part_id": parts["DEMO-PART-CMP-210"].id, "item_name_snapshot": parts["DEMO-PART-CMP-210"].part_name, "item_number_snapshot": parts["DEMO-PART-CMP-210"].part_code, "item_version_snapshot": "A", "quantity": Decimal("4"), "quantity_unit_id": units["DEMO-U-PCS"].id, "is_outsourced": 0, "sort_no": 3, "remark": TAG}, result)

    for code in ["DEMO-PART-ASM-100", "DEMO-PART-ASM-200", "DEMO-PART-CMP-110", "DEMO-PART-CMP-120", "DEMO-PART-CMP-210", "DEMO-PART-CMP-220"]:
        p = parts[code]
        for fn, ft in [(f"{code}_drawing.pdf", "pdf"), (f"{code}_process.xlsx", "xlsx")]:
            get_or_create(session, PartAttachment, and_(PartAttachment.part_id == p.id, PartAttachment.file_name == fn),
                {"part_id": p.id, "file_name": fn, "file_url": f"https://example.com/files/{fn}", "file_type": ft, "file_size": 204800, "source_type": "UPLOAD"}, result)


def count_rows(session, model, clause) -> int:
    return len(list(session.scalars(select(model).where(clause)).all()))


def main():
    result = SeedResult()
    with SessionLocal() as session:
        units, currencies, regions = seed_base(session, result)
        cats, mats = seed_materials(session, units, currencies, regions, result)
        seed_equipment(session, currencies, units, result)
        seed_parts_bom_attachment(session, units, cats, mats, result)
        session.commit()

        print("=== INDUSTRIAL DEMO DATA SEEDED ===")
        print(f"created={result.created}, reused={result.reused}")
        print(f"units_demo={count_rows(session, Unit, Unit.unit_code.like('DEMO-U-%'))}")
        print(f"currencies={count_rows(session, Currency, Currency.currency_code.in_(['CNY','USD','EUR']))}")
        print(f"exchange_rates_demo={count_rows(session, CurrencyExchangeRate, CurrencyExchangeRate.source_name == 'IDME-DEMO')}")
        print(f"regions_demo={count_rows(session, Region, Region.remark == TAG)}")
        print(f"region_cost_profiles_demo={count_rows(session, RegionCostProfile, RegionCostProfile.profile_code.like('DEMO-RCP-%'))}")
        print(f"material_categories_demo={count_rows(session, MaterialCategory, MaterialCategory.category_code.like('DEMO-CAT-%'))}")
        print(f"materials_demo={count_rows(session, Material, Material.material_code.like('DEMO-MAT-%'))}")
        print(f"material_prices_demo={count_rows(session, MaterialPrice, MaterialPrice.source_name == 'IDME-DEMO')}")
        print(f"equipment_categories_demo={count_rows(session, EquipmentCategory, EquipmentCategory.category_code.like('DEMO-ECAT-%'))}")
        print(f"equipments_demo={count_rows(session, Equipment, Equipment.equipment_code.like('DEMO-EQ-%'))}")
        print(f"equipment_rates_demo={count_rows(session, EquipmentRate, EquipmentRate.rate_code.like('DEMO-ER-%'))}")
        print(f"equipment_cost_profiles_demo={count_rows(session, EquipmentCostProfile, EquipmentCostProfile.profile_name.like('DEMO-ECP-%'))}")
        print(f"material_types_demo={count_rows(session, MaterialType, MaterialType.material_type_code.like('DEMO-MT-%'))}")
        print(f"parts_demo={count_rows(session, Part, Part.part_code.like('DEMO-PART-%'))}")
        print(f"boms_demo={count_rows(session, Bom, Bom.bom_code.like('DEMO-BOM-%'))}")
        print(f"bom_items_demo={count_rows(session, BomItem, BomItem.remark == TAG)}")
        print(f"attachments_demo={count_rows(session, PartAttachment, PartAttachment.file_name.like('DEMO-PART-%'))}")


if __name__ == "__main__":
    main()
