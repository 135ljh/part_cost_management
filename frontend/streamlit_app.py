import io
import json
import os
import re
from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import pandas as pd
import requests
import streamlit as st


# ---------------------------------------------------------------------
# Streamlit compatibility helpers
# ---------------------------------------------------------------------
if not hasattr(st, "rerun") and hasattr(st, "experimental_rerun"):
    st.rerun = st.experimental_rerun

if not hasattr(st, "fragment"):
    def _fragment(*args, **kwargs):
        def _decorator(func):
            return func
        return _decorator
    st.fragment = _fragment

if not hasattr(st, "dialog"):
    def _dialog(*args, **kwargs):
        def _decorator(func):
            return func
        return _decorator
    st.dialog = _dialog


def _st_toggle(label: str, value: bool = False, key: str | None = None):
    if hasattr(st, "toggle"):
        return st.toggle(label, value=value, key=key)
    return st.checkbox(label, value=value, key=key)


st.set_page_config(page_title="IDME Data Configuration Center", page_icon="🛠️", layout="wide")

# =====================================================================
# 顶级工业级数据管理系统 (Enterprise PLM / IDME) 核心样式注入
# 放弃消费级圆角渐变，采用高密度、严谨、硬朗的工业控制面板风格
# =====================================================================
st.markdown(
    """
    <style>
    /* 引入 IBM Plex 工业级无衬线与等宽字体 */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
      --idme-bg: #f3f4f6; /* 工业基础灰 */
      --idme-panel: #ffffff;
      --idme-border: #d1d5db;
      --idme-text-main: #111827;
      --idme-text-sub: #4b5563;
      --idme-primary: #005abb; /* 工业级深蓝 (Siemens/Dassault常用) */
      --idme-sidebar: #1e293b; /* 深灰侧边栏 */
      --idme-sidebar-text: #e2e8f0;
      --idme-accent: #0284c7;
    }

    /* 强制全局工业字体与背景 */
    html, body, [class*="css"] {
      font-family: 'IBM Plex Sans', -apple-system, sans-serif !important;
      color: var(--idme-text-main);
    }
    
    .stApp {
      background-color: var(--idme-bg);
    }

    /* 隐藏 Streamlit 默认头部元素，提升沉浸感 */
    header[data-testid="stHeader"] { background: transparent !important; }
    
    /* --- 重构侧边栏 (暗色工业控制台风格) --- */
    [data-testid="stSidebar"] {
        background-color: var(--idme-sidebar) !important;
        border-right: 1px solid #0f172a !important;
    }
    [data-testid="stSidebar"] * { color: var(--idme-sidebar-text) !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 0.9rem !important; }
    
    /* --- 页面主标题 (工业面板风格) --- */
    .hero {
      background: var(--idme-panel);
      border: 1px solid var(--idme-border);
      border-left: 6px solid var(--idme-primary);
      padding: 20px 28px;
      border-radius: 2px; /* 极小圆角，工业硬朗感 */
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      margin-bottom: 24px;
      margin-top: 10px;
    }
    .hero h1 { 
        margin: 0; 
        font-size: 1.6rem !important; 
        font-weight: 600 !important; 
        color: var(--idme-text-main) !important; 
        letter-spacing: -0.01em;
    }
    .hero p { 
        margin: 8px 0 0 0; 
        color: var(--idme-text-sub); 
        font-size: 0.95rem; 
    }

    /* --- 模块导航卡片 --- */
    .module-card {
      border: 1px solid var(--idme-border);
      border-top: 3px solid var(--idme-border);
      background: var(--idme-panel);
      padding: 16px 20px;
      min-height: 140px;
      transition: all 0.15s ease-in-out;
      border-radius: 2px;
    }
    .module-card:hover {
      border-top: 3px solid var(--idme-primary);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }
    .module-card h4 { 
        margin: 0 0 8px 0; 
        color: var(--idme-primary) !important; 
        font-size: 1.1rem !important; 
        font-weight: 600;
    }
    .module-card p { 
        margin: 0; 
        color: var(--idme-text-sub); 
        font-size: 0.85rem; 
        line-height: 1.4; 
    }

    /* --- 顶部遥测数据面板 (Telemetry Data) --- */
    .stat-box {
      background: var(--idme-panel);
      border: 1px solid var(--idme-border);
      border-radius: 2px;
      padding: 14px 20px;
      position: relative;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .stat-k { 
        color: #6b7280; 
        font-size: 0.75rem; 
        font-weight: 600; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
    }
    /* 数据使用等宽字体，专业感极强 */
    .stat-v { 
        color: var(--idme-text-main); 
        font-size: 1.6rem; 
        font-weight: 500; 
        margin-top: 6px; 
        font-family: 'IBM Plex Mono', monospace; 
    }

    /* --- 详情页字段面板 --- */
    .field-card {
      background: #fafafa;
      border-bottom: 1px solid #e5e7eb;
      padding: 10px 14px;
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .field-k { color: #6b7280; font-size: 0.85rem; font-weight: 500; }
    .field-v { color: #111827; font-size: 0.9rem; font-family: 'IBM Plex Mono', monospace; }

    /* --- 按钮硬朗化 --- */
    div.stButton > button, div.stDownloadButton > button {
      border-radius: 2px !important;
      border: 1px solid var(--idme-border) !important;
      color: #374151 !important;
      background: #ffffff !important;
      font-weight: 500 !important;
      font-size: 0.9rem !important;
      padding: 0.25rem 0.75rem !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
      border-color: #9ca3af !important;
      background: #f3f4f6 !important;
    }
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
      border: 1px solid var(--idme-primary) !important;
      color: #ffffff !important;
      background: var(--idme-primary) !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover {
      background: #004a99 !important;
    }

    /* --- 表单输入框紧凑化 --- */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 2px !important;
        border: 1px solid var(--idme-border) !important;
        background-color: #ffffff !important;
        font-size: 0.9rem !important;
        font-family: 'IBM Plex Mono', monospace !important; /* 输入框采用等宽 */
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: var(--idme-primary) !important;
        box-shadow: 0 0 0 1px var(--idme-primary) !important;
    }
    
    /* 缩小页面边距，提高数据密度 */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; max-width: 95% !important;}
    
    /* Tabs 样式修正 */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid var(--idme-border); }
    .stTabs [data-baseweb="tab"] { padding-top: 8px; padding-bottom: 8px; }
    .stTabs [aria-selected="true"] { border-bottom-color: var(--idme-primary) !important; color: var(--idme-primary) !important;}
    </style>
    """,
    unsafe_allow_html=True,
)


def m(name: str, group: str, desc: str, endpoint: str, summary: list[str], fields: list[dict[str, Any]], tree_endpoint: str | None = None) -> dict[str, Any]:
    data = {
        "name": name,
        "group": group,
        "description": desc,
        "endpoint": endpoint,
        "summary_fields": summary,
        "fields": fields,
    }
    if tree_endpoint:
        data["tree_endpoint"] = tree_endpoint
    return data


MODULES: dict[str, dict[str, Any]] = {
    "units": m("单位配置", "基础主数据", "计量单位与换算系数。", "/api/v1/units", ["unit_name", "unit_code", "unit_category"], [
        {"name": "unit_code", "label": "单位编码", "type": "string", "required": True},
        {"name": "unit_name", "label": "单位名称", "type": "string", "required": True},
        {"name": "unit_display_name", "label": "显示名", "type": "string"},
        {"name": "unit_category", "label": "单位类别", "type": "string", "required": True},
        {"name": "measurement_system", "label": "度量系统", "type": "string"},
        {"name": "base_unit_id", "label": "基准单位", "type": "fk", "target": "units"},
        {"name": "unit_factor", "label": "换算系数", "type": "decimal", "required": True, "default": "1"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "currencies": m("货币配置", "基础主数据", "币种与ISO代码。", "/api/v1/currencies", ["currency_name", "currency_code", "currency_symbol"], [
        {"name": "currency_code", "label": "ISO代码", "type": "string", "required": True},
        {"name": "currency_name", "label": "货币名称", "type": "string", "required": True},
        {"name": "currency_symbol", "label": "符号", "type": "string"},
        {"name": "precision_scale", "label": "精度", "type": "int", "default": 2},
        {"name": "is_base_currency", "label": "基准货币", "type": "bool", "default": False},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "exchange_rates": m("汇率配置", "基础主数据", "货币对汇率维护。", "/api/v1/exchange-rates", ["rate_type", "from_currency_id", "to_currency_id", "exchange_rate"], [
        {"name": "from_currency_id", "label": "源货币", "type": "fk", "target": "currencies", "required": True},
        {"name": "to_currency_id", "label": "目标货币", "type": "fk", "target": "currencies", "required": True},
        {"name": "rate_type", "label": "汇率类型", "type": "string", "required": True, "default": "FIXED"},
        {"name": "exchange_rate", "label": "汇率值", "type": "decimal", "required": True},
        {"name": "effective_date", "label": "生效时间", "type": "datetime", "required": True},
        {"name": "source_name", "label": "来源", "type": "string"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "regions": m("区域配置", "基础主数据", "国家/省/市/区县/街道。", "/api/v1/regions", ["region_name", "region_code", "region_type", "level_no"], [
        {"name": "region_code", "label": "区域编码", "type": "string", "required": True},
        {"name": "region_name", "label": "区域名称", "type": "string", "required": True},
        {"name": "region_type", "label": "区域类型", "type": "string", "required": True},
        {"name": "parent_id", "label": "上级区域", "type": "fk", "target": "regions"},
        {"name": "level_no", "label": "层级深度", "type": "int", "default": 1},
        {"name": "full_name", "label": "全路径", "type": "string"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "region_cost_profiles": m("区域成本配置", "成本基础", "人工福利与水电煤租金。", "/api/v1/region-cost-profiles", ["profile_name", "supplier_name", "region_id", "currency_id"], [
        {"name": "profile_name", "label": "配置名称", "type": "string", "required": True},
        {"name": "region_id", "label": "区域", "type": "fk", "target": "regions", "required": True},
        {"name": "supplier_name", "label": "工厂名称", "type": "string"},
        {"name": "supplier_code", "label": "工厂编号", "type": "string"},
        {"name": "currency_id", "label": "基础货币", "type": "fk", "target": "currencies", "required": True},
        {"name": "operating_worker_rate", "label": "操作工人", "type": "decimal", "default": "0"},
        {"name": "skilled_worker_rate", "label": "技术工人", "type": "decimal", "default": "0"},
        {"name": "transfer_technician_rate", "label": "调机技术员", "type": "decimal", "default": "0"},
        {"name": "production_leader_rate", "label": "生产领班", "type": "decimal", "default": "0"},
        {"name": "inspector_rate", "label": "检验员", "type": "decimal", "default": "0"},
        {"name": "engineer_rate", "label": "工程师", "type": "decimal", "default": "0"},
        {"name": "mold_fitter_rate", "label": "模具钳工", "type": "decimal", "default": "0"},
        {"name": "cost_interest_rate", "label": "财务成本利率", "type": "decimal", "default": "0"},
        {"name": "benefits_one_shift", "label": "福利(一班制)", "type": "decimal", "default": "0"},
        {"name": "benefits_two_shift", "label": "福利(两班制)", "type": "decimal", "default": "0"},
        {"name": "benefits_three_shift", "label": "福利(三班制)", "type": "decimal", "default": "0"},
        {"name": "factory_rent", "label": "厂房租金", "type": "decimal", "default": "0"},
        {"name": "office_fee", "label": "办公区域", "type": "decimal", "default": "0"},
        {"name": "electricity_fee", "label": "电费", "type": "decimal", "default": "0"},
        {"name": "water_fee", "label": "水费", "type": "decimal", "default": "0"},
        {"name": "gas_fee", "label": "煤气", "type": "decimal", "default": "0"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
}

# second bundle modules
MODULES.update({
    "equipment_categories": m("设备分类配置", "设备基础", "设备分类树。", "/api/v1/equipment-categories", ["category_name", "category_code", "parent_id"], [
        {"name": "category_name", "label": "分类名称", "type": "string", "required": True},
        {"name": "category_code", "label": "分类编码", "type": "string"},
        {"name": "parent_id", "label": "父分类", "type": "fk", "target": "equipment_categories"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "equipment": m("设备配置", "设备基础", "设备主数据。", "/api/v1/equipment", ["equipment_name", "equipment_code", "equipment_type", "category_id"], [
        {"name": "equipment_code", "label": "设备编号", "type": "string", "required": True},
        {"name": "equipment_name", "label": "设备名称", "type": "string", "required": True},
        {"name": "category_id", "label": "设备分类", "type": "fk", "target": "equipment_categories"},
        {"name": "equipment_type", "label": "设备类型", "type": "string"},
        {"name": "manufacturer", "label": "制造商", "type": "string"},
        {"name": "energy_type", "label": "能源类型", "type": "string"},
        {"name": "specification_text", "label": "规格说明", "type": "string"},
        {"name": "scale_desc", "label": "规模描述", "type": "string"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "equipment_specifications": m("设备规格配置", "设备基础", "设备规格K-V。", "/api/v1/equipment-specifications", ["equipment_id", "spec_key", "spec_value"], [
        {"name": "equipment_id", "label": "设备", "type": "fk", "target": "equipment", "required": True},
        {"name": "spec_key", "label": "规格项", "type": "string", "required": True},
        {"name": "spec_value", "label": "规格值", "type": "string", "required": True},
        {"name": "spec_unit_id", "label": "规格单位", "type": "fk", "target": "units"},
        {"name": "sort_no", "label": "排序号", "type": "int", "default": 1},
    ]),
    "equipment_rates": m("设备费率配置", "设备成本", "设备费率与人工负担。", "/api/v1/equipment-rates", ["rate_code", "equipment_number", "equipment_type", "total_minute_rate"], [
        {"name": "rate_code", "label": "费率编码", "type": "string"},
        {"name": "equipment_number", "label": "设备编号", "type": "string"},
        {"name": "equipment_category_name", "label": "设备类别", "type": "string"},
        {"name": "description", "label": "设备描述", "type": "string"},
        {"name": "equipment_type", "label": "设备类型", "type": "string"},
        {"name": "manpower", "label": "人力", "type": "int", "default": 0},
        {"name": "labor_group", "label": "劳动力组", "type": "string"},
        {"name": "direct_labor", "label": "直接人工", "type": "decimal", "default": "0"},
        {"name": "direct_fringe", "label": "附加直接人工", "type": "decimal", "default": "0"},
        {"name": "indirect_labor", "label": "间接人工", "type": "decimal", "default": "0"},
        {"name": "indirect_fringe", "label": "附加间接人工", "type": "decimal", "default": "0"},
        {"name": "total_labor", "label": "总人工", "type": "decimal", "default": "0"},
        {"name": "depreciation", "label": "折旧", "type": "decimal", "default": "0"},
        {"name": "insurance", "label": "保险", "type": "decimal", "default": "0"},
        {"name": "floor_space", "label": "楼面面积", "type": "decimal", "default": "0"},
        {"name": "mro_labor", "label": "维护人工", "type": "decimal", "default": "0"},
        {"name": "utilities", "label": "水电煤", "type": "decimal", "default": "0"},
        {"name": "indirect_materials", "label": "间接材料", "type": "decimal", "default": "0"},
        {"name": "other_burden", "label": "其他费用", "type": "decimal", "default": "0"},
        {"name": "total_burden", "label": "总和(其他费用)", "type": "decimal", "default": "0"},
        {"name": "total_minute_rate", "label": "每分钟费用", "type": "decimal", "default": "0"},
        {"name": "investment", "label": "投入", "type": "decimal", "default": "0"},
        {"name": "currency_id", "label": "币种", "type": "fk", "target": "currencies"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "equipment_cost_profiles": m("设备成本配置", "设备成本", "设备资本成本快照。", "/api/v1/equipment-cost-profiles", ["profile_name", "equipment_id", "currency_id", "hourly_rate"], [
        {"name": "equipment_id", "label": "设备", "type": "fk", "target": "equipment", "required": True},
        {"name": "profile_name", "label": "配置名称", "type": "string", "required": True},
        {"name": "currency_id", "label": "币种", "type": "fk", "target": "currencies", "required": True},
        {"name": "equipment_number_snapshot", "label": "设备编号快照", "type": "string"},
        {"name": "manufacturer_snapshot", "label": "制造商快照", "type": "string"},
        {"name": "hourly_rate", "label": "小时费率", "type": "decimal", "default": "0"},
        {"name": "equipment_cost", "label": "设备成本", "type": "decimal", "default": "0"},
        {"name": "investment", "label": "投入", "type": "decimal", "default": "0"},
        {"name": "asset_status", "label": "资产状态", "type": "string"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "material_categories": m("物质分类配置", "物质基础", "物质分类树。", "/api/v1/material-categories", ["category_name", "category_code", "parent_id"], [
        {"name": "category_name", "label": "分类名称", "type": "string", "required": True},
        {"name": "category_code", "label": "分类编码", "type": "string"},
        {"name": "parent_id", "label": "父分类", "type": "fk", "target": "material_categories"},
        {"name": "category_type", "label": "分类类型", "type": "string", "default": "SUBSTANCE"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ], tree_endpoint="/api/v1/material-categories/tree/all"),
    "materials": m("物质配置", "物质基础", "物质主数据。", "/api/v1/materials", ["material_name", "material_code", "category_id", "density"], [
        {"name": "material_name", "label": "物质名称", "type": "string", "required": True},
        {"name": "material_code", "label": "物质编码", "type": "string"},
        {"name": "category_id", "label": "物质分类", "type": "fk", "target": "material_categories"},
        {"name": "density", "label": "密度", "type": "decimal"},
        {"name": "density_unit_id", "label": "密度单位", "type": "fk", "target": "units"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "material_prices": m("物质价格配置", "物质基础", "物质价格维护。", "/api/v1/material-prices", ["material_id", "unit_price", "currency_id", "region_id"], [
        {"name": "material_id", "label": "物质", "type": "fk", "target": "materials", "required": True},
        {"name": "region_id", "label": "区域", "type": "fk", "target": "regions"},
        {"name": "supplier_name", "label": "供应商", "type": "string"},
        {"name": "currency_id", "label": "币种", "type": "fk", "target": "currencies", "required": True},
        {"name": "price_unit_id", "label": "价格单位", "type": "fk", "target": "units", "required": True},
        {"name": "unit_price", "label": "单价", "type": "decimal", "required": True},
        {"name": "source_name", "label": "来源", "type": "string"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
})

# =====================================================================
# 全新模块：零件管理 (Part Management)
# =====================================================================
MODULES.update({
    "material_types": m("物料类型", "零件管理", "定义零件的物料分类字典。", "/api/v1/material-types", ["material_type_name", "material_type_code"], [
        {"name": "material_type_code", "label": "物料编码", "type": "string", "required": True},
        {"name": "material_type_name", "label": "物料名称", "type": "string", "required": True},
        {"name": "description", "label": "描述", "type": "string"},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "parts": m("零件主数据", "零件管理", "企业核心业务对象：零件台账维护。", "/api/v1/parts", ["part_code", "part_name", "part_type", "material_type_id", "part_status", "revision_no"], [
        {"name": "part_code", "label": "零件编号", "type": "string", "required": True},
        {"name": "part_name", "label": "零件名称", "type": "string", "required": True},
        {"name": "part_description", "label": "零件描述", "type": "string"},
        {"name": "part_type", "label": "零件类型", "type": "string"},
        {"name": "material_category_id", "label": "物料分类", "type": "fk", "target": "material_categories"},
        {"name": "material_type_id", "label": "物料类型", "type": "fk", "target": "material_types"},
        {"name": "preferred_material_id", "label": "默认物料", "type": "fk", "target": "materials"},
        {"name": "quantity_unit_id", "label": "数量单位", "type": "fk", "target": "units"},
        {"name": "surface_area", "label": "表面积", "type": "decimal"},
        {"name": "volume", "label": "体积", "type": "decimal"},
        {"name": "cad_file_url", "label": "CAD文件地址", "type": "string"},
        {"name": "target_url", "label": "跳转地址", "type": "string"},
        {"name": "legacy_result", "label": "旧系统结果", "type": "string"},
        {"name": "legacy_msg", "label": "旧系统消息", "type": "string"},
        {"name": "part_status", "label": "业务状态", "type": "string", "default": "DRAFT"},
        {"name": "lifecycle_stage", "label": "生命周期", "type": "string", "default": "DESIGN"},
        {"name": "revision_no", "label": "修订版次", "type": "string", "default": "A"},
        {"name": "version_no", "label": "版本号", "type": "int", "default": 1},
        {"name": "is_active", "label": "启用", "type": "bool", "default": True},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "boms": m("BOM头配置", "零件管理", "父零件BOM版本头信息。", "/api/v1/boms", ["bom_code", "bom_name", "part_id", "version_no", "status"], [
        {"name": "part_id", "label": "父零件", "type": "fk", "target": "parts", "required": True},
        {"name": "bom_code", "label": "BOM编码", "type": "string", "required": True},
        {"name": "bom_name", "label": "BOM名称", "type": "string"},
        {"name": "version_no", "label": "版本号", "type": "string", "default": "V1"},
        {"name": "status", "label": "状态", "type": "string", "default": "DRAFT"},
        {"name": "effective_from", "label": "生效开始", "type": "datetime"},
        {"name": "effective_to", "label": "生效结束", "type": "datetime"},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "bom_items": m("BOM明细配置", "零件管理", "父子件关系与用量明细。", "/api/v1/bom-items", ["bom_id", "child_part_id", "quantity", "quantity_unit_id"], [
        {"name": "bom_id", "label": "所属BOM", "type": "fk", "target": "boms", "required": True},
        {"name": "parent_item_id", "label": "父级明细", "type": "fk", "target": "bom_items"},
        {"name": "child_part_id", "label": "子零件", "type": "fk", "target": "parts", "required": True},
        {"name": "item_name_snapshot", "label": "名称快照", "type": "string"},
        {"name": "item_number_snapshot", "label": "编码快照", "type": "string"},
        {"name": "item_version_snapshot", "label": "版本快照", "type": "string"},
        {"name": "quantity", "label": "用量", "type": "decimal", "required": True, "default": "1"},
        {"name": "quantity_unit_id", "label": "数量单位", "type": "fk", "target": "units"},
        {"name": "is_outsourced", "label": "是否外协", "type": "bool", "default": False},
        {"name": "sort_no", "label": "排序号", "type": "int", "default": 1},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
    "part_attachments": m("零件附件", "零件管理", "零件图纸/文档等附件台账。", "/api/v1/part-attachments", ["part_id", "file_name", "file_type", "source_type"], [
        {"name": "part_id", "label": "所属零件", "type": "fk", "target": "parts", "required": True},
        {"name": "file_name", "label": "文件名", "type": "string", "required": True},
        {"name": "file_url", "label": "文件地址", "type": "string", "required": True},
        {"name": "file_type", "label": "文件类型", "type": "string"},
        {"name": "file_size", "label": "文件大小(字节)", "type": "int"},
        {"name": "source_type", "label": "来源类型", "type": "string", "default": "UPLOAD"},
    ]),
    "cost_items": m("成本计算", "零件管理", "零件成本计算记录与分析结果。", "/api/v1/cost-items", ["calculation_name", "part_id", "total_cost", "currency_id", "unit_id"], [
        {"name": "calculation_name", "label": "计算名称", "type": "string", "required": True},
        {"name": "part_id", "label": "零件", "type": "fk", "target": "parts", "required": True},
        {"name": "currency_id", "label": "货币单位", "type": "fk", "target": "currencies", "required": True},
        {"name": "unit_id", "label": "数量单位", "type": "fk", "target": "units"},
        {"name": "material_cost", "label": "材料成本", "type": "decimal", "required": True, "default": "0"},
        {"name": "manufacturing_cost", "label": "制造成本", "type": "decimal", "required": True, "default": "0"},
        {"name": "overhead_cost", "label": "间接费用", "type": "decimal", "required": True, "default": "0"},
        {"name": "total_cost", "label": "总成本", "type": "decimal", "required": True, "default": "0"},
        {"name": "rule_version", "label": "规则版本", "type": "string", "default": "v1"},
        {"name": "trace_detail", "label": "计算追溯详情", "type": "string"},
        {"name": "remark", "label": "备注", "type": "string"},
    ]),
})

FORM_GROUPS: dict[str, list[tuple[str, list[str]]]] = {
    "region_cost_profiles": [
        ("基础信息", ["profile_name", "region_id", "supplier_name", "supplier_code", "currency_id"]),
        ("人工费率", ["operating_worker_rate", "skilled_worker_rate", "transfer_technician_rate", "production_leader_rate", "inspector_rate", "engineer_rate", "mold_fitter_rate"]),
        ("福利与费用", ["cost_interest_rate", "benefits_one_shift", "benefits_two_shift", "benefits_three_shift", "factory_rent", "office_fee", "electricity_fee", "water_fee", "gas_fee"]),
        ("状态信息", ["is_active", "remark"]),
    ],
    "equipment_rates": [
        ("设备信息", ["rate_code", "equipment_number", "equipment_category_name", "description", "equipment_type"]),
        ("人工成本", ["manpower", "labor_group", "direct_labor", "direct_fringe", "indirect_labor", "indirect_fringe", "total_labor"]),
        ("负担成本", ["depreciation", "insurance", "floor_space", "mro_labor", "utilities", "indirect_materials", "other_burden", "total_burden", "total_minute_rate", "investment"]),
        ("状态信息", ["currency_id", "is_active", "remark"]),
    ],
    "materials": [
        ("核心信息", ["material_name", "material_code", "category_id"]),
        ("理化属性", ["density", "density_unit_id"]),
        ("状态信息", ["is_active", "remark"]),
    ],
    "material_types": [
        ("基本信息", ["material_type_code", "material_type_name", "description"]),
        ("状态与备注", ["is_active", "remark"]),
    ],
    "parts": [
        ("核心属性", ["part_code", "part_name", "part_type", "part_description", "material_category_id", "material_type_id"]),
        ("物料与计量", ["preferred_material_id", "quantity_unit_id", "surface_area", "volume"]),
        ("扩展集成字段", ["cad_file_url", "target_url", "legacy_result", "legacy_msg"]),
        ("生命周期与版本", ["part_status", "lifecycle_stage", "revision_no", "version_no"]),
        ("状态与备注", ["is_active", "remark"]),
    ],
    "boms": [
        ("基础信息", ["part_id", "bom_code", "bom_name", "version_no", "status"]),
        ("生效窗口", ["effective_from", "effective_to"]),
        ("状态与备注", ["remark"]),
    ],
    "bom_items": [
        ("父子关系", ["bom_id", "parent_item_id", "child_part_id"]),
        ("快照与计量", ["item_name_snapshot", "item_number_snapshot", "item_version_snapshot", "quantity", "quantity_unit_id"]),
        ("属性信息", ["is_outsourced", "sort_no", "remark"]),
    ],
    "part_attachments": [
        ("基础信息", ["part_id", "file_name", "file_type", "source_type"]),
        ("文件信息", ["file_url", "file_size"]),
    ],
    "cost_items": [
        ("基础变量", ["calculation_name", "part_id", "currency_id", "unit_id", "rule_version"]),
        ("成本结果", ["material_cost", "manufacturing_cost", "overhead_cost", "total_cost"]),
        ("追溯与备注", ["trace_detail", "remark"]),
    ],
}

def _init_state() -> None:
    defaults = {
        "page_key": "overview_home",
        "search_text": "",
        "api_base_url": os.getenv("IDME_API_BASE_URL", "http://127.0.0.1:8001"),
        "reload_token": 0,
        "logs": [],
        "part_bom_part_id": None,
        "part_bom_part_label": "",
        "part_attachment_part_id": None,
        "part_cost_part_id": None,
        "part_cost_item_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _base_url() -> str:
    return st.session_state.api_base_url.rstrip("/")

def _backend_ok(base: str) -> bool:
    try:
        resp = requests.get(f"{base.rstrip('/')}/health", timeout=1.5)
        return resp.status_code < 500
    except requests.RequestException:
        return False

def _autofix_api_base_url() -> None:
    current = _base_url()
    if _backend_ok(current):
        return
    for base in ("http://127.0.0.1:8001", "http://127.0.0.1:8000"):
        if base.rstrip("/") == current.rstrip("/"):
            continue
        if _backend_ok(base):
            st.session_state.api_base_url = base
            break

def _log(module: str, action: str, ok: bool, message: str, row_id: Any | None = None) -> None:
    st.session_state.logs.insert(
        0,
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "module": module,
            "action": action,
            "status": "成功" if ok else "失败",
            "row_id": row_id,
            "message": message,
        },
    )
    st.session_state.logs = st.session_state.logs[:500]

@st.cache_data(show_spinner=False, ttl=20)
def _cached_get(base: str, path: str, token: int) -> tuple[bool, Any]:
    try:
        resp = requests.get(f"{base}{path}", timeout=15)
        if resp.status_code >= 400:
            try:
                return False, f"{resp.status_code}: {resp.json()}"
            except Exception:
                return False, f"{resp.status_code}: {resp.text}"
        return True, resp.json()
    except requests.RequestException as exc:
        return False, str(exc)

def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[bool, Any]:
    try:
        resp = requests.request(method, f"{_base_url()}{path}", json=payload, timeout=20)
        if resp.status_code >= 400:
            try:
                return False, f"{resp.status_code}: {resp.json()}"
            except Exception:
                return False, f"{resp.status_code}: {resp.text}"
        if resp.status_code == 204:
            return True, None
        return True, resp.json()
    except requests.RequestException as exc:
        return False, str(exc)

def _clear_cache() -> None:
    st.session_state.reload_token += 1

def _load_rows(path: str) -> tuple[bool, Any]:
    return _cached_get(_base_url(), path, st.session_state.reload_token)

def _label_for_row(module_key: str, row: dict[str, Any]) -> str:
    keys = MODULES[module_key]["summary_fields"]
    preferred = [k for k in keys if not k.endswith("_id")]
    backup = [k for k in keys if k.endswith("_id")]
    parts = [str(row.get(k)) for k in preferred if row.get(k) not in ("", None)]
    if not parts:
        parts = [str(row.get(k)) for k in backup if row.get(k) not in ("", None)]
    return " | ".join(parts[:3]) if parts else f"ID {row.get('id')}"

def _field_label_map(module_key: str) -> dict[str, str]:
    labels = {f["name"]: f.get("label", f["name"]) for f in MODULES[module_key]["fields"]}
    common = {
        "id": "ID",
        "created_at": "创建时间",
        "updated_at": "更新时间",
        "created_by": "创建人", "updated_by": "更新人", "is_deleted": "是否删除",
        "delete_flag": "删除标记",
        "part_code": "零件编码",
        "part_name": "零件名称",
        "material_type_name": "物料类型名称",
        "material_category_name": "物料分类名称",
        "preferred_material_name": "默认物料名称",
        "quantity_unit_name": "数量单位名称",
        "child_part_code": "子件编码",
        "child_part_name": "子件名称",
        "technical_reliability": "技术可靠性", "acquisition_value": "购置价值", "number_of_equipment": "设备数量",
        "annual_production_hours": "年生产小时", "equipment_efficiency": "设备效率",
        "installation_expenses": "安装费用",
        "foundation_expenses": "基础费用",
        "other_expenses": "其他费用",
        "residual_value": "残值", "equipment_lifespan_years": "设备寿命(年)",
        "estimated_depreciation": "预计折旧",
        "interest_rate": "利率",
        "total_area_required": "总需求面积", "production_site_cost": "生产场地成本",
        "rated_power": "额定功率",
        "electricity_usage_ratio": "用电比例",
        "power_cost_electricity": "电力成本",
        "maintenance_cost": "维护成本",
        "auxiliary_material_cost": "辅助材料成本",
        "total_fixed_cost": "总固定成本", "total_variable_cost": "总变动成本", "cost_per_unit_time": "单位时间成本",
        "asset_status": "资产状态", "effective_from": "生效开始", "effective_to": "生效结束",
        "direct_labor": "直接人工",
        "direct_fringe": "直接附加人工",
        "indirect_labor": "间接人工",
        "indirect_fringe": "间接附加人工",
        "total_labor": "人工合计",
        "depreciation": "折旧",
        "insurance": "保险",
        "floor_space": "楼面成本",
        "mro_labor": "维护人工",
        "utilities": "公用耗能", "indirect_materials": "间接材料",
        "other_burden": "其他负担",
        "total_burden": "负担合计",
        "total_minute_rate": "每分钟费率",
        "calculation_name": "计算名称",
        "material_cost": "材料成本",
        "manufacturing_cost": "制造成本", "overhead_cost": "间接费用",
        "total_cost": "总成本", "rule_version": "规则版本",
        "trace_detail": "追溯详情",
        "currency_code": "货币编码",
        "unit_code": "单位编码",
    }
    for k, v in common.items():
        labels.setdefault(k, v)
    return labels

def _auto_cn_label(col: str) -> str:
    token_map = {
        "id": "ID", "part": "零件", "bom": "BOM", "item": "明细", "material": "物料",
        "type": "类型", "category": "分类", "name": "名称", "code": "编码",
        "description": "描述", "remark": "备注", "status": "状态", "lifecycle": "生命周期",
        "stage": "阶段", "version": "版本", "revision": "修订", "no": "号", "quantity": "数量",
        "unit": "单位", "price": "价格", "rate": "费率", "cost": "成本", "profile": "配置",
        "region": "区域", "currency": "币种", "exchange": "汇率", "effective": "生效",
        "from": "开始", "to": "结束", "parent": "父级", "child": "子级", "source": "来源",
        "file": "文件", "size": "大小", "url": "链接", "created": "创建", "updated": "更新",
        "by": "人", "is": "是否", "active": "启用", "total": "总", "direct": "直接",
        "indirect": "间接", "labor": "人工", "hourly": "每小时", "minute": "每分钟", "spec": "规格",
        "value": "值", "sort": "排序", "density": "密度", "volume": "体积", "surface": "表面",
        "target": "目标", "legacy": "旧系统", "result": "结果", "msg": "消息", "manufacturer": "制造商",
        "energy": "能源", "equipment": "设备", "supplier": "供应商", "display": "显示", "system": "系统",
        "factor": "系数", "full": "完整", "level": "层级", "technical": "技术", "reliability": "可靠性",
        "number": "数量", "acquisition": "购置", "annual": "年度", "production": "生产", "hours": "小时",
        "installation": "安装", "expenses": "费用", "foundation": "基础", "residual": "残值", "lifespan": "寿命",
        "years": "年", "estimated": "预计", "depreciation": "折旧", "interest": "利息", "area": "面积",
        "required": "需求", "site": "场地", "electricity": "电力", "usage": "使用", "ratio": "比例",
        "maintenance": "维护", "auxiliary": "辅助", "fixed": "固定", "variable": "变动", "per": "每", "time": "时间",
    }
    parts = [p for p in col.split("_") if p]
    if not parts:
        return "字段"
    zh_parts = [token_map.get(p, p.upper() if p.isupper() else p) for p in parts]
    return "".join(zh_parts)

def _col_label(module_key: str, col: str) -> str:
    labels = _field_label_map(module_key)
    if col in labels:
        return labels[col]
    return _auto_cn_label(col)

def _build_col_maps(module_key: str, columns: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    c2l: dict[str, str] = {}
    l2c: dict[str, str] = {}
    counts: dict[str, int] = {}
    for col in columns:
        base_label = _col_label(module_key, col)
        counts[base_label] = counts.get(base_label, 0) + 1
        label = base_label if counts[base_label] == 1 else f"{base_label}{counts[base_label]}"
        c2l[col] = label
        l2c[label] = col
    return c2l, l2c

def _fk_options(module_key: str) -> list[tuple[int | None, str]]:
    ok, data = _load_rows(MODULES[module_key]["endpoint"])
    if not ok:
        return [(None, f"加载失败: {data}")]
    rows = data or []
    opts = [(None, "-- 请选择 --")]
    for row in rows:
        opts.append((row.get("id"), _label_for_row(module_key, row)))
    return opts

def _fk_display_maps(module_key: str) -> dict[str, dict[Any, str]]:
    maps: dict[str, dict[Any, str]] = {}
    for field in MODULES[module_key]["fields"]:
        if field.get("type") != "fk":
            continue
        target = field.get("target")
        if not target or target not in MODULES:
            continue
        ok, data = _load_rows(MODULES[target]["endpoint"])
        if not ok:
            continue
        id_map: dict[Any, str] = {}
        for row in data or []:
            rid = row.get("id")
            if rid is None:
                continue
            label = _label_for_row(target, row)
            id_map[rid] = label
            id_map[str(rid)] = label
        maps[field["name"]] = id_map
    return maps

def _apply_fk_display(module_key: str, item: dict[str, Any], fk_maps: dict[str, dict[Any, str]]) -> dict[str, Any]:
    shown = dict(item)
    for field_name, id_map in fk_maps.items():
        if field_name not in shown:
            continue
        raw = shown.get(field_name)
        if raw in (None, ""):
            continue
        shown[field_name] = id_map.get(raw, id_map.get(str(raw), raw))
    return shown

def _normalize(ftype: str, raw: Any) -> tuple[Any, str | None]:
    if ftype == "bool":
        return bool(raw), None
    if raw in ("", None):
        return None, None
    if ftype in ("int", "fk"):
        try:
            return int(raw), None
        except Exception:
            return None, "必须是整数"
    if ftype == "decimal":
        try:
            return float(raw), None
        except Exception:
            return None, "必须是数字"
    if ftype == "datetime":
        try:
            datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            return str(raw), None
        except Exception:
            return None, "时间格式应为 YYYY-MM-DDTHH:MM:SS"
    return raw, None

def _field_widget(module_key: str, field: dict[str, Any], source: dict[str, Any] | None, key: str) -> Any:
    name = field["name"]
    label = field["label"]
    v0 = source.get(name) if source else field.get("default")
    t = field["type"]

    if t == "bool":
        return _st_toggle(label, value=bool(v0) if v0 is not None else False, key=key)
    if t == "fk":
        options = _fk_options(field["target"])
        ids = [x[0] for x in options]
        labels = [x[1] for x in options]
        idx = ids.index(v0) if v0 in ids else 0
        label_chosen = st.selectbox(label, labels, index=idx, key=key)
        return ids[labels.index(label_chosen)]
    if t == "int":
        v = int(v0) if isinstance(v0, int) else int(field.get("default", 0))
        return st.number_input(label, value=v, step=1, key=key)
    placeholder = "YYYY-MM-DDTHH:MM:SS" if t == "datetime" else ""
    return st.text_input(label, value="" if v0 is None else str(v0), placeholder=placeholder, key=key)

def _build_payload(module_key: str, form_values: dict[str, Any], mode: str, source: dict[str, Any] | None) -> tuple[dict[str, Any], str | None]:
    payload: dict[str, Any] = {}
    for field in MODULES[module_key]["fields"]:
        name = field["name"]
        new_value, err = _normalize(field["type"], form_values.get(name))
        if err:
            return {}, f"{field['label']}{err}"
        if mode == "create":
            if field.get("required") and new_value is None:
                return {}, f"{field['label']} 不能为空"
            if new_value is not None:
                payload[name] = new_value
        else:
            old_value = source.get(name) if source else None
            if str(old_value) != str(new_value):
                payload[name] = new_value
    return payload, None

def _detail_view(module_key: str, item: dict[str, Any]) -> None:
    fk_maps = _fk_display_maps(module_key)
    item = _apply_fk_display(module_key, item, fk_maps)
    labels = _field_label_map(module_key)
    ordered_keys = [f["name"] for f in MODULES[module_key]["fields"] if f["name"] in item]
    ordered_keys.extend([k for k in item.keys() if k not in ordered_keys])
    cols = st.columns(2)
    i = 0
    for k in ordered_keys:
        v = item.get(k)
        if isinstance(v, bool):
            v = "是" if v else "否"
        k_show = labels.get(k, _col_label(module_key, k))
        with cols[i % 2]:
            st.markdown(
                f"<div class='field-card'><div class='field-k'>{k_show}</div><div class='field-v'>{'-' if v is None else v}</div></div>",
                unsafe_allow_html=True,
            )
        i += 1

def _open_dialog(module_key: str, mode: str, item: dict[str, Any] | None = None) -> None:
    title = MODULES[module_key]["name"]

    if mode == "detail":
        @st.dialog(f"详情面板 - {title}", width="large")
        def _dlg_detail() -> None:
            _detail_view(module_key, item or {})
            if st.button("关闭", use_container_width=True):
                st.rerun()
        _dlg_detail()
        return

    if mode == "delete":
        @st.dialog(f"危险操作确认 - {title}", width="small")
        def _dlg_delete() -> None:
            st.warning("删除后不可恢复，请确认未被其他业务对象关联。")
            c1, c2 = st.columns(2)
            if c1.button("确认删除", use_container_width=True):
                ok, resp = _request("DELETE", f"{MODULES[module_key]['endpoint']}/{item['id']}")
                _log(title, "删除", ok, "删除成功" if ok else str(resp), item.get("id"))
                if ok:
                    _clear_cache()
                    st.success("记录已清除。")
                    st.rerun()
                st.error(resp)
            if c2.button("取消", use_container_width=True):
                st.rerun()
        _dlg_delete()
        return

    @st.dialog(f"{'新建记录' if mode == 'create' else '编辑记录'} - {title}", width="large")
    def _dlg_form() -> None:
        fields = MODULES[module_key]["fields"]
        groups = FORM_GROUPS.get(
            module_key,
            [("基础参数", [f["name"] for f in fields[:6]]), ("扩展参数", [f["name"] for f in fields[6:]])],
        )
        field_map = {f["name"]: f for f in fields}
        values: dict[str, Any] = {}

        with st.form(key=f"form_{module_key}_{mode}_{item.get('id') if item else 'new'}"):
            idx = 0
            for gtitle, names in groups:
                names = [n for n in names if n in field_map]
                if not names:
                    continue
                with st.expander(gtitle, expanded=(gtitle == groups[0][0])):
                    c1, c2 = st.columns(2)
                    for name in names:
                        field = field_map[name]
                        with c1 if idx % 2 == 0 else c2:
                            values[name] = _field_widget(module_key, field, item, f"{module_key}_{mode}_{name}_{idx}")
                        idx += 1

            b1, b2 = st.columns(2)
            submit = b1.form_submit_button("执行写入", type="primary", use_container_width=True)
            cancel = b2.form_submit_button("放弃修改", use_container_width=True)
            if cancel:
                st.rerun()
            if submit:
                payload, err = _build_payload(module_key, values, mode, item)
                if err:
                    st.error(err)
                    return
                if mode == "edit" and not payload:
                    st.warning("系统未检测到字段变更。")
                    return
                if mode == "create":
                    ok, resp = _request("POST", MODULES[module_key]["endpoint"], payload)
                else:
                    ok, resp = _request("PUT", f"{MODULES[module_key]['endpoint']}/{item['id']}", payload)
                _log(title, "新增" if mode == "create" else "修改", ok, "保存成功" if ok else str(resp), item.get("id") if item else None)
                if ok:
                    _clear_cache()
                    st.success("数据写入成功。")
                    st.rerun()
                st.error(resp)
    _dlg_form()

def _apply_table_filters(df: pd.DataFrame, module_key: str) -> pd.DataFrame:
    with st.expander("数据视图配置 (过滤 & 排序)", expanded=False):
        all_cols = list(df.columns)
        c2l, l2c = _build_col_maps(module_key, all_cols)
        label_cols = [c2l[c] for c in all_cols]
        chosen_labels = st.multiselect("激活过滤器列", label_cols, key=f"fcols_{module_key}")
        for label in chosen_labels:
            col = l2c[label]
            values = sorted([str(v) for v in df[col].dropna().unique().tolist()][:300])
            pick = st.multiselect(f"{label} 条件", values, key=f"fvals_{module_key}_{col}")
            if pick:
                df = df[df[col].astype(str).isin(pick)]
        c1, c2 = st.columns(2)
        sort_label = c1.selectbox("主排序列", ["(默认不排序)"] + label_cols, key=f"sortcol_{module_key}")
        asc = c2.toggle("升序排列", value=False, key=f"sortasc_{module_key}")
        if sort_label != "(默认不排序)":
            sort_col = l2c[sort_label]
            df = df.sort_values(by=sort_col, ascending=asc, kind="stable")
    return df

def _export_import_tools(module_key: str, rows: list[dict[str, Any]]) -> None:
    st.markdown("##### 批量数据管道 (Data Pipeline)")
    df = pd.DataFrame(rows)
    c1, c2, c3 = st.columns(3)
    c1.download_button("下载 CSV 报表", df.to_csv(index=False).encode("utf-8-sig"), file_name=f"{module_key}.csv", mime="text/csv", use_container_width=True)
    excel_io = io.BytesIO()
    with pd.ExcelWriter(excel_io, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="data")
    c2.download_button(
        "下载 Excel 报表",
        excel_io.getvalue(),
        file_name=f"{module_key}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    upload = c3.file_uploader("上传 CSV/Excel 文件进行装载", type=["csv", "xlsx"], key=f"u_{module_key}")
    if upload is not None and st.button("开始装载数据", key=f"do_import_{module_key}", use_container_width=True):
        imp_df = pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)
        records = imp_df.fillna("").to_dict(orient="records")
        ok_cnt, fail_cnt = 0, 0
        for rec in records:
            payload = {k: (None if v == "" else v) for k, v in rec.items()}
            ok, resp = _request("POST", MODULES[module_key]["endpoint"], payload)
            _log(MODULES[module_key]["name"], "批量装载", ok, "装载成功" if ok else str(resp), payload.get("id"))
            if ok:
                ok_cnt += 1
            else:
                fail_cnt += 1
        _clear_cache()
        st.success(f"批处理完成：成功入库 {ok_cnt} 条，失败 {fail_cnt} 条")

def _render_tree(module_key: str) -> None:
    path = MODULES[module_key].get("tree_endpoint")
    if not path:
        st.info("系统提示：当前配置对象无层级结构。")
        return
    ok, data = _load_rows(path)
    if not ok:
        st.error(f"层级数据加载失败：{data}")
        return
    if not data:
        st.info("层级结构暂无实例数据。")
        return

    def walk(node: dict[str, Any], depth: int = 0) -> None:
        indent = "  " * depth
        st.markdown(f"{indent}- **{node.get('category_name')}** (UID: {node.get('id')})")
        for m_item in node.get("materials", []):
            st.markdown(f"{indent}  - {m_item.get('material_name')} (UID: {m_item.get('id')})")
        for child in node.get("children", []):
            walk(child, depth + 1)

    for root in data:
        walk(root)

@st.fragment(run_every="1s")
def _live_time_stat() -> None:
    st.markdown(
        f"<div class='stat-box'><div class='stat-k'>本地系统时钟</div><div class='stat-v'>{datetime.now().strftime('%H:%M:%S')}</div></div>",
        unsafe_allow_html=True,
    )

def _render_module(module_key: str) -> None:
    cfg = MODULES[module_key]
    is_part = cfg["group"] == "零件管理"

    parent_key = "overview_parts" if is_part else "overview_data"
    parent_label = "⚙️ 零件管理大盘" if is_part else "⊞ 数据配置大盘"

    if st.button(f"← 返回 {parent_label}", key=f"back_{module_key}"):
        st.session_state.page_key = parent_key
        st.session_state.search_text = ""
        st.rerun()

    st.markdown(
        f"""
        <div class="hero">
          <h1>{cfg['name']}</h1>
          <p>{cfg['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if module_key == "part_attachments" and st.session_state.get("part_attachment_part_id"):
        pc1, pc2 = st.columns([0.8, 0.2])
        pc1.info(f"当前仅显示零件ID={st.session_state.part_attachment_part_id} 的附件。")
        if pc2.button("清除过滤", use_container_width=True):
            st.session_state.part_attachment_part_id = None
            st.rerun()
    if module_key == "cost_items" and st.session_state.get("part_cost_part_id"):
        pc1, pc2 = st.columns([0.8, 0.2])
        pc1.info(f"当前仅显示零件ID={st.session_state.part_cost_part_id} 的成本记录。")
        if pc2.button("清除过滤", use_container_width=True):
            st.session_state.part_cost_part_id = None
            st.rerun()

    c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
    st.session_state.search_text = c1.text_input("全文检索", value=st.session_state.search_text, placeholder="输入配置项标识、名称等...")
    if c2.button("同步后端数据", use_container_width=True):
        _clear_cache()
        st.rerun()
    if c3.button("新增配置对象", type="primary", use_container_width=True):
        _open_dialog(module_key, "create")

    if module_key == "part_attachments" and st.session_state.get("part_attachment_part_id"):
        ok, data = _load_rows(f"/api/v1/part-attachments/part/{st.session_state.part_attachment_part_id}")
    elif module_key == "cost_items" and st.session_state.get("part_cost_part_id"):
        ok, all_data = _load_rows(cfg["endpoint"])
        if ok:
            data = [x for x in (all_data or []) if int(x.get("part_id") or 0) == int(st.session_state.part_cost_part_id)]
        else:
            data = all_data
    else:
        ok, data = _load_rows(cfg["endpoint"])
        
    if not ok:
        st.error(f"连接 API 失败：{data}")
        return
    rows: list[dict[str, Any]] = data or []

    total = len(rows)
    active = sum(1 for r in rows if r.get("is_active") in (True, 1, "1"))
    s1, s2, s3 = st.columns(3)
    s1.markdown(f"<div class='stat-box'><div class='stat-k'>对象总数 (Total records)</div><div class='stat-v'>{total}</div></div>", unsafe_allow_html=True)
    s2.markdown(f"<div class='stat-box'><div class='stat-k'>活跃状态 (Active status)</div><div class='stat-v'>{active}</div></div>", unsafe_allow_html=True)
    with s3:
        _live_time_stat()

    tabs = ["配置数据表", "批处理任务"]
    if module_key == "material_categories":
        tabs.append("BOM/层级结构树")
    t = st.tabs(tabs)

    with t[0]:
        if not rows:
            st.info("系统提示：当前配置模块下暂无数据。")
        else:
            fk_maps = _fk_display_maps(module_key)
            display_rows = [_apply_fk_display(module_key, r, fk_maps) for r in rows]
            df = pd.DataFrame(display_rows)
            q = st.session_state.search_text.strip().lower()
            if q:
                df = df[df.apply(lambda row: q in " ".join([str(x) for x in row.values if x is not None]).lower(), axis=1)]
            df = _apply_table_filters(df, module_key)
            if df.empty:
                st.warning("检索结果为空。")
            else:
                all_cols = list(df.columns)
                c2l, l2c = _build_col_maps(module_key, all_cols)
                label_cols = [c2l[c] for c in all_cols]
                default_labels = label_cols[: min(12, len(label_cols))]
                display_labels = st.multiselect("自定义视图列", label_cols, default=default_labels, key=f"viewcols_{module_key}")
                display_cols = [l2c[x] for x in display_labels] if display_labels else all_cols
                if "id" in df.columns and "id" not in display_cols:
                    display_cols = ["id"] + display_cols
                view_df = df[display_cols].copy()
                rename_map, _ = _build_col_maps(module_key, list(view_df.columns))
                view_df = view_df.rename(columns=rename_map)
                select_col = "选取"
                view_df.insert(0, select_col, False)
                edited = st.data_editor(
                    view_df,
                    hide_index=True,
                    use_container_width=True,
                    disabled=[c for c in view_df.columns if c != select_col],
                    key=f"grid_{module_key}_{st.session_state.reload_token}",
                )
                selected = edited[edited[select_col] == True]
                
                if module_key == "parts":
                    b1, b2, b3, b4, b5, b6, b7 = st.columns([0.20, 0.12, 0.12, 0.12, 0.15, 0.14, 0.15])
                else:
                    b1, b2, b3, b4 = st.columns([0.4, 0.2, 0.2, 0.2])
                    
                if selected.empty:
                    b1.info("请在表格左侧勾选对象进行操作。")
                else:
                    id_label = rename_map.get("id", "id")
                    sid = int(selected.iloc[0][id_label]) if id_label in selected.columns else None
                    row_obj = next((r for r in rows if r.get("id") == sid), None)
                    b1.success(f"当前锁定对象 UID: {sid}")
                    if b2.button("对象详情", use_container_width=True, key=f"detail_{module_key}"):
                        _open_dialog(module_key, "detail", row_obj)
                    if b3.button("编辑属性", use_container_width=True, key=f"edit_{module_key}"):
                        _open_dialog(module_key, "edit", row_obj)
                    if b4.button("移除对象", use_container_width=True, key=f"del_{module_key}"):
                        _open_dialog(module_key, "delete", row_obj)
                        
                    if module_key == "parts":
                        if b5.button("BOM详情", use_container_width=True, key=f"bom_{module_key}"):
                            st.session_state.part_bom_part_id = sid
                            st.session_state.part_bom_part_label = f"{row_obj.get('part_code', '')} | {row_obj.get('part_name', '')}" if row_obj else str(sid)
                            st.session_state.page_key = "part_bom_detail"
                            st.rerun()
                        if b6.button("附件", use_container_width=True, key=f"att_{module_key}"):
                            st.session_state.part_attachment_part_id = sid
                            st.session_state.page_key = "part_attachments"
                            st.session_state.search_text = ""
                            st.rerun()
                        if b7.button("成本分析", use_container_width=True, key=f"cost_{module_key}"):
                            st.session_state.part_cost_part_id = sid
                            st.session_state.part_cost_item_id = None
                            st.session_state.page_key = "part_cost_list"
                            st.session_state.search_text = ""
                            st.rerun()

    with t[1]:
        _export_import_tools(module_key, rows)

    if module_key == "material_categories" and len(t) > 2:
        with t[2]:
            _render_tree(module_key)

def _render_part_bom_detail() -> None:
    part_id = st.session_state.get("part_bom_part_id")
    if not part_id:
        st.warning("未指定零件，请从零件列表中选择后进入 BOM 详情。")
        if st.button("返回零件管理大盘", use_container_width=True):
            st.session_state.page_key = "overview_parts"
            st.rerun()
        return

    if st.button("← 返回零件主数据", use_container_width=True):
        st.session_state.page_key = "parts"
        st.session_state.search_text = ""
        st.rerun()

    ok, resp = _request("GET", f"/api/v1/boms/part/{part_id}/detail")
    if not ok:
        st.error(f"BOM详情加载失败：{resp}")
        return

    part_code = resp.get("part_code", "")
    part_name = resp.get("part_name", "")
    st.markdown(
        f"""
        <div class="hero">
          <h1>BOM详情 - {part_name}</h1>
          <p>父零件：{part_code} (ID: {part_id})。展示该零件当前BOM版本下的子件构成与用量。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bom = resp.get("bom")
    items = resp.get("items") or []
    if not bom:
        st.info("该零件当前尚未配置 BOM 头信息。请先在“BOM头配置”模块中创建。")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='stat-box'><div class='stat-k'>BOM编码</div><div class='stat-v'>{bom.get('bom_code') or '-'}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='stat-box'><div class='stat-k'>版本号</div><div class='stat-v'>{bom.get('version_no') or '-'}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='stat-box'><div class='stat-k'>状态</div><div class='stat-v'>{bom.get('status') or '-'}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='stat-box'><div class='stat-k'>子件数</div><div class='stat-v'>{len(items)}</div></div>", unsafe_allow_html=True)
    st.write("")

    if not items:
        st.info("当前 BOM 暂无子件明细。")
        return

    id_to_children: dict[int, list[dict[str, Any]]] = {}
    roots: list[dict[str, Any]] = []
    for item in items:
        pid = item.get("parent_item_id")
        if pid in (None, 0):
            roots.append(item)
            continue
        id_to_children.setdefault(int(pid), []).append(item)

    def _node_text(item: dict[str, Any]) -> str:
        part_name = item.get("child_part_name") or "-"
        part_code = item.get("child_part_code") or "N/A"
        qty = item.get("quantity")
        unit = item.get("quantity_unit_name") or ""
        unit_txt = f" {unit}" if unit else ""
        mode = "外协" if item.get("is_outsourced") in (True, 1, "1") else "自制"
        return f"{part_name} ({part_code}) x {qty}{unit_txt} [{mode}]"

    lines: list[str] = []

    def _append_tree_lines(nodes: list[dict[str, Any]], prefix: str = "") -> None:
        for i, node in enumerate(nodes):
            is_last = i == len(nodes) - 1
            branch = "└── " if is_last else "├── "
            lines.append(f"{prefix}{branch}{_node_text(node)}")
            children = sorted(
                id_to_children.get(int(node.get("id")), []),
                key=lambda x: (x.get("sort_no") or 0, x.get("id") or 0),
            )
            if children:
                next_prefix = f"{prefix}{'    ' if is_last else '│   '}"
                _append_tree_lines(children, next_prefix)

    sorted_roots = sorted(roots, key=lambda x: (x.get("sort_no") or 0, x.get("id") or 0))
    _append_tree_lines(sorted_roots)

    st.markdown("#### BOM分类树")
    st.code("\n".join(lines) if lines else "(空)", language="text")

    st.markdown("#### BOM明细表")
    df = pd.DataFrame(items)
    show_cols = [c for c in ["id", "parent_item_id", "child_part_code", "child_part_name", "quantity", "quantity_unit_name", "is_outsourced", "sort_no", "remark"] if c in df.columns]
    rename = {
        "id": "明细ID",
        "parent_item_id": "父明细ID",
        "child_part_code": "子件编码",
        "child_part_name": "子件名称",
        "quantity": "用量",
        "quantity_unit_name": "数量单位",
        "is_outsourced": "外协",
        "sort_no": "排序",
        "remark": "备注",
    }
    st.dataframe(df[show_cols].rename(columns=rename), use_container_width=True, hide_index=True)


def _parse_cost_trace(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("trace_detail")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}

def _save_cost_trace(row: dict[str, Any], trace: dict[str, Any], extra: dict[str, Any] | None = None) -> tuple[bool, Any]:
    payload: dict[str, Any] = {
        "trace_detail": json.dumps(trace, ensure_ascii=False),
    }
    if extra:
        payload.update(extra)
    return _request("PUT", f"/api/v1/cost-items/{row['id']}", payload)

def _render_part_cost_list() -> None:
    part_id = st.session_state.get("part_cost_part_id")
    if not part_id:
        st.warning("未指定零件，请先在零件列表中选择。")
        if st.button("返回零件列表", key="pcost_list_back_parts"):
            st.session_state.page_key = "parts"
            st.rerun()
        return

    if st.button("← 返回零件列表", key="pcost_list_back", use_container_width=True):
        st.session_state.page_key = "parts"
        st.rerun()

    ok_part, parts_data = _load_rows("/api/v1/parts")
    part = next((x for x in (parts_data or []) if int(x.get("id") or 0) == int(part_id)), {}) if ok_part else {}
    part_code = part.get("part_code") or str(part_id)
    part_name = part.get("part_name") or f"Part-{part_id}"

    st.markdown(
        f"""
        <div class="hero">
          <h1>成本计算列表</h1>
          <p>零件：{part_name} ({part_code})</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([0.45, 0.2, 0.35])
    q = c1.text_input("计算名称", key=f"pcost_q_{part_id}")
    do_new = c2.button("新建", type="primary", key=f"pcost_new_{part_id}", use_container_width=True)
    if c3.button("刷新", key=f"pcost_refresh_{part_id}", use_container_width=True):
        _clear_cache()
        st.rerun()

    if do_new:
        @st.dialog("新建成本计算", width="large")
        def _dlg_new() -> None:
            calc_name = st.text_input("计算名称", value=f"{part_code}-成本计算", key=f"dlg_new_name_{part_id}")
            ccy_opts = [x for x in _fk_options("currencies") if x[0] is not None]
            unit_opts = [x for x in _fk_options("units") if x[0] is not None]
            cc = st.selectbox("货币单位", [x[1] for x in ccy_opts], key=f"dlg_new_cc_{part_id}")
            uu = st.selectbox("数量单位", [x[1] for x in unit_opts], key=f"dlg_new_uu_{part_id}")
            b1, b2 = st.columns(2)
            if b1.button("确认新建", type="primary", key=f"dlg_new_ok_{part_id}", use_container_width=True):
                payload = {
                    "calculation_name": calc_name,
                    "part_id": int(part_id),
                    "currency_id": int(next(x[0] for x in ccy_opts if x[1] == cc)),
                    "unit_id": int(next(x[0] for x in unit_opts if x[1] == uu)),
                    "material_cost": 0,
                    "manufacturing_cost": 0,
                    "overhead_cost": 0,
                    "total_cost": 0,
                    "rule_version": "material_v1",
                    "remark": "新建空白计算",
                }
                ok, resp = _request("POST", "/api/v1/cost-items", payload)
                if ok:
                    st.session_state.part_cost_item_id = resp.get("id")
                    _clear_cache()
                    st.success("新建成功")
                    st.rerun()
                st.error(resp)
            if b2.button("取消", key=f"dlg_new_cancel_{part_id}", use_container_width=True):
                st.rerun()
        _dlg_new()

    ok_rows, rows = _load_rows("/api/v1/cost-items")
    if not ok_rows:
        st.error(rows)
        return

    data = [x for x in (rows or []) if int(x.get("part_id") or 0) == int(part_id)]
    if q:
        ql = q.strip().lower()
        data = [x for x in data if ql in str(x.get("calculation_name") or "").lower()]
    data = sorted(data, key=lambda x: str(x.get("created_at") or ""), reverse=True)

    if not data:
        st.info("当前零件暂无成本计算记录。")
        return

    df = pd.DataFrame([
        {"选取": False, "id": r.get("id"), "计算名称": r.get("calculation_name"), "零件编号": r.get("part_code"), "零件名称": r.get("part_name"), "成本": r.get("total_cost"), "货币单位": r.get("currency_code"), "数量单位": r.get("unit_code"), "创建时间": r.get("created_at")}
        for r in data
    ])
    edited = st.data_editor(df, hide_index=True, use_container_width=True, disabled=[c for c in df.columns if c != "选取"], key=f"pcost_grid_{part_id}_{st.session_state.reload_token}")
    selected = edited[edited["选取"] == True]

    b1, b2, b3, b4 = st.columns([0.4, 0.2, 0.2, 0.2])
    if selected.empty:
        b1.info("请先选择一条记录。")
        return

    sid = int(selected.iloc[0]["id"])
    obj = next((r for r in data if int(r.get("id") or 0) == sid), None)
    b1.success(f"当前锁定计算 ID: {sid}")

    if b2.button("详情", key=f"pcost_detail_btn_{sid}", use_container_width=True):
        st.session_state.part_cost_item_id = sid
        st.session_state.page_key = "part_cost_detail"
        st.rerun()

    if b3.button("修改", key=f"pcost_edit_btn_{sid}", use_container_width=True):
        @st.dialog("修改成本计算", width="large")
        def _dlg_edit() -> None:
            name = st.text_input("计算名称", value=obj.get("calculation_name") if obj else "", key=f"dlg_edit_name_{sid}")
            remark = st.text_input("备注", value=obj.get("remark") if obj else "", key=f"dlg_edit_remark_{sid}")
            x1, x2 = st.columns(2)
            if x1.button("保存修改", type="primary", key=f"dlg_edit_ok_{sid}", use_container_width=True):
                ok_u, resp_u = _request("PUT", f"/api/v1/cost-items/{sid}", {"calculation_name": name, "remark": remark})
                if ok_u:
                    _clear_cache()
                    st.success("修改成功")
                    st.rerun()
                st.error(resp_u)
            if x2.button("取消", key=f"dlg_edit_cancel_{sid}", use_container_width=True):
                st.rerun()
        _dlg_edit()

    if b4.button("删除", key=f"pcost_del_btn_{sid}", use_container_width=True):
        @st.dialog("删除确认", width="small")
        def _dlg_del() -> None:
            st.warning("删除后不可恢复，是否继续？")
            x1, x2 = st.columns(2)
            if x1.button("确认删除", type="primary", key=f"dlg_del_ok_{sid}", use_container_width=True):
                ok_d, resp_d = _request("DELETE", f"/api/v1/cost-items/{sid}")
                if ok_d:
                    if st.session_state.get("part_cost_item_id") == sid:
                        st.session_state.part_cost_item_id = None
                    _clear_cache()
                    st.success("删除成功")
                    st.rerun()
                st.error(resp_d)
            if x2.button("取消", key=f"dlg_del_cancel_{sid}", use_container_width=True):
                st.rerun()
        _dlg_del()

def _render_part_cost_detail() -> None:
    part_id = st.session_state.get("part_cost_part_id")
    item_id = st.session_state.get("part_cost_item_id")

    if not part_id:
        st.warning("未指定零件，请先从零件列表进入。")
        if st.button("返回零件列表", key="pcost_detail_back_parts"):
            st.session_state.page_key = "parts"
            st.rerun()
        return

    if not item_id:
        ok_latest, latest = _request("GET", f"/api/v1/cost-items/part/{part_id}/latest")
        if ok_latest and latest:
            item_id = latest.get("id")
            st.session_state.part_cost_item_id = item_id
        else:
            st.info("当前零件暂无成本计算记录。")
            if st.button("进入成本计算列表", key="pcost_to_list"):
                st.session_state.page_key = "part_cost_list"
                st.rerun()
            return

    ok_item, row = _request("GET", f"/api/v1/cost-items/{item_id}")
    if not ok_item:
        st.error(row)
        return

    ok_part, parts_data = _load_rows("/api/v1/parts")
    part = next((x for x in (parts_data or []) if int(x.get("id") or 0) == int(part_id)), {}) if ok_part else {}
    part_code = part.get("part_code") or str(part_id)
    part_name = part.get("part_name") or f"Part-{part_id}"

    if st.button("← 返回成本计算列表", key=f"pcost_back_{part_id}", use_container_width=True):
        st.session_state.page_key = "part_cost_list"
        st.rerun()

    total_cost = float(row.get("total_cost") or 0)
    currency_code = row.get("currency_code")
    unit_code = row.get("unit_code")
    currency_name = row.get("currency_name")
    unit_name = row.get("unit_name")

    if not currency_code:
        ok_ccy, ccy_rows = _load_rows("/api/v1/currencies")
        if ok_ccy:
            cobj = next((x for x in (ccy_rows or []) if int(x.get("id") or 0) == int(row.get("currency_id") or 0)), None)
            if cobj:
                currency_code = cobj.get("currency_code")
                currency_name = cobj.get("currency_name")

    if not unit_code:
        ok_unit, unit_rows = _load_rows("/api/v1/units")
        if ok_unit:
            uobj = next((x for x in (unit_rows or []) if int(x.get("id") or 0) == int(row.get("unit_id") or 0)), None)
            if uobj:
                unit_code = uobj.get("unit_code")
                unit_name = uobj.get("unit_name")

    ccy = currency_code or "CNY"
    unit = unit_code or "件"

    def _contains_zh(s: str) -> bool:
        return any("\u4e00" <= ch <= "\u9fff" for ch in (s or ""))

    def _currency_cn_name(code: str, name: str | None) -> str:
        nm = str(name or "").strip()
        if nm and _contains_zh(nm):
            return nm
        mapping = {
            "CNY": "人民币", "RMB": "人民币", "USD": "美元",
            "EUR": "欧元", "JPY": "日元", "GBP": "英镑", "HKD": "港币",
        }
        candidate = nm.upper() if nm else str(code).upper()
        return mapping.get(candidate, mapping.get(str(code).upper(), str(code)))

    def _unit_cn_name(code: str, name: str | None) -> str:
        nm = str(name or "").strip()
        if nm and _contains_zh(nm):
            return nm

        src = nm if nm else str(code or "")
        uc = src.upper()
        tail = uc.split("-")[-1] if "-" in uc else uc
        mapping = {
            "PCS": "件", "EA": "件", "PC": "件", "KG": "千克",
            "G": "克", "M": "米", "MM": "毫米", "CM": "厘米",
            "L": "升", "H": "小时", "MIN": "分钟", "S": "秒",
        }
        if tail in mapping:
            return mapping[tail]
        if uc in mapping:
            return mapping[uc]

        m = re.search(r"(PCS|EA|PC|KG|G|M|MM|CM|L|H|MIN|S)$", uc)
        if m:
            return mapping.get(m.group(1), str(code))
        return str(code)

    ccy_cn = _currency_cn_name(ccy, currency_name)
    unit_cn = _unit_cn_name(unit, unit_name)
    st.markdown(
        f"""
        <div class="hero">
          <h1>{row.get('calculation_name') or '未命名计算'}</h1>
          <p>{part_name} ({part_code}) | 总成本 {total_cost:.2f} {ccy_cn}/{unit_cn}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    trace = _parse_cost_trace(row)
    key_prefix = f"pcostd_{item_id}"
    tabs = st.tabs(["基础数据", "材料成本", "制造成本", "间接费用", "成本明细", "结果分析"])

    with tabs[0]:
        base = trace.get("base_data", {}) if isinstance(trace, dict) else {}
        calc = base.get("calculation_variables", {})
        prod = base.get("production", {})

        ccy_opts = _fk_options("currencies")
        unit_opts = _fk_options("units")
        region_opts = _fk_options("regions")

        ccy_ids = [x[0] for x in ccy_opts]
        unit_ids = [x[0] for x in unit_opts]
        region_ids = [x[0] for x in region_opts]
        ccy_labels = [x[1] for x in ccy_opts]
        unit_labels = [x[1] for x in unit_opts]
        region_labels = [x[1] for x in region_opts]

        left, right = st.columns(2)
        left.markdown("#### 计算变量")
        calc_name = left.text_input("计算名称", value=row.get("calculation_name") or "", key=f"{key_prefix}_calc_name")

        region_value = calc.get("region_id")
        region_idx = region_ids.index(region_value) if region_value in region_ids else 0
        region_label = left.selectbox("地区", region_labels, index=region_idx, key=f"{key_prefix}_region")
        region_id = region_ids[region_labels.index(region_label)]

        unit_value = row.get("unit_id")
        unit_idx = unit_ids.index(unit_value) if unit_value in unit_ids else 0
        unit_label = left.selectbox("单位", unit_labels, index=unit_idx, key=f"{key_prefix}_unit")
        unit_id = unit_ids[unit_labels.index(unit_label)]

        ccy_value = row.get("currency_id")
        ccy_idx = ccy_ids.index(ccy_value) if ccy_value in ccy_ids else 0
        ccy_label = left.selectbox("货币", ccy_labels, index=ccy_idx, key=f"{key_prefix}_currency")
        currency_id = ccy_ids[ccy_labels.index(ccy_label)]

        procurement_type = left.selectbox("采购类型", ["采购", "自制"], index=0 if calc.get("procurement_type", "采购") == "采购" else 1, key=f"{key_prefix}_proc_type")

        default_shifts = int(calc.get("shifts_per_day", 3) or 3)
        default_hours = float(calc.get("hours_per_shift", 8) or 8)
        default_days = float(calc.get("days_per_week", 5) or 5)
        default_extra = float(calc.get("extra_shift_per_week", 0) or 0)
        default_weeks = float(calc.get("weeks_per_year", 48) or 48)
        annual_effective_hours = float(calc.get("annual_effective_hours", (default_shifts * default_days + default_extra) * default_hours * default_weeks))
        annual_effective_hours = float(st.session_state.get(f"{key_prefix}_annual_effective_hours", annual_effective_hours))

        hh1, hh2 = left.columns([0.7, 0.3])
        hh1.metric("每年有效小时数", f"{annual_effective_hours:.2f}")
        if hh2.button("计算", key=f"{key_prefix}_open_hours", use_container_width=True):
            @st.dialog("每年有效小时数计算器", width="large")
            def _dlg_hours() -> None:
                shifts_per_day = st.selectbox("每天生产班次", [1, 2, 3, 4], index=max(0, min(3, default_shifts - 1)), key=f"{key_prefix}_dlg_shifts")
                hours_per_shift = st.number_input("每班生产小时数", min_value=0.0, value=float(default_hours), step=0.5, key=f"{key_prefix}_dlg_hps")
                days_per_week = st.number_input("每周生产天数", min_value=0.0, value=float(default_days), step=1.0, key=f"{key_prefix}_dlg_dpw")
                extra_shift_per_week = st.number_input("每周额外换班次数", min_value=0.0, value=float(default_extra), step=1.0, key=f"{key_prefix}_dlg_extra")
                weeks_per_year = st.number_input("每年生产周数", min_value=0.0, value=float(default_weeks), step=1.0, key=f"{key_prefix}_dlg_wpy")

                weekly_shift_count = shifts_per_day * days_per_week + extra_shift_per_week
                annual_days = days_per_week * weeks_per_year
                annual_hours_calc = weekly_shift_count * hours_per_shift * weeks_per_year

                st.number_input("每周换班次数", value=float(weekly_shift_count), disabled=True, key=f"{key_prefix}_dlg_weekly")
                st.number_input("每年生产天数", value=float(annual_days), disabled=True, key=f"{key_prefix}_dlg_days")
                st.number_input("每年有效小时数", value=float(annual_hours_calc), disabled=True, key=f"{key_prefix}_dlg_hours")

                x1, x2 = st.columns(2)
                if x1.button("确定", type="primary", key=f"{key_prefix}_dlg_ok", use_container_width=True):
                    st.session_state[f"{key_prefix}_annual_effective_hours"] = float(annual_hours_calc)
                    st.session_state[f"{key_prefix}_shifts_per_day"] = int(shifts_per_day)
                    st.session_state[f"{key_prefix}_hours_per_shift"] = float(hours_per_shift)
                    st.session_state[f"{key_prefix}_days_per_week"] = float(days_per_week)
                    st.session_state[f"{key_prefix}_extra_shift_per_week"] = float(extra_shift_per_week)
                    st.session_state[f"{key_prefix}_weeks_per_year"] = float(weeks_per_year)

                    trace.setdefault("base_data", {})
                    trace["base_data"].setdefault("calculation_variables", {})
                    trace["base_data"]["calculation_variables"].update({
                        "annual_effective_hours": float(annual_hours_calc),
                        "shifts_per_day": int(shifts_per_day),
                        "hours_per_shift": float(hours_per_shift),
                        "days_per_week": float(days_per_week),
                        "extra_shift_per_week": float(extra_shift_per_week),
                        "weeks_per_year": float(weeks_per_year),
                    })
                    _save_cost_trace(row, trace)
                    _clear_cache()
                    st.rerun()
                if x2.button("取消", key=f"{key_prefix}_dlg_cancel", use_container_width=True):
                    st.rerun()
            _dlg_hours()

        net_sale_price = left.number_input("净售价", min_value=0.0, value=float(calc.get("net_sale_price", 0) or 0), step=1.0, key=f"{key_prefix}_net_sale")

        right.markdown("#### 生产数量")
        qualified_annual_demand = right.number_input("合格品年需求量", min_value=0.0, value=float(prod.get("qualified_annual_demand", 0) or 0), step=1.0, key=f"{key_prefix}_qualified")
        annual_other_demand = right.number_input("年其它需求量", min_value=0.0, value=float(prod.get("annual_other_demand", 0) or 0), step=1.0, key=f"{key_prefix}_other")
        batch_no = right.text_input("制造批次号", value=str(prod.get("manufacturing_batch_no", "") or ""), key=f"{key_prefix}_batch")
        lifecycle_years = right.number_input("零件生命周期", min_value=0.0, value=float(prod.get("part_lifecycle_years", 0) or 0), step=1.0, key=f"{key_prefix}_life")
        prod_date = right.date_input("生产开始日期", value=pd.to_datetime(prod.get("production_start_date") or "2025-12-01").date(), key=f"{key_prefix}_start_date")

        if st.button("保存基础数据", type="primary", key=f"{key_prefix}_save_base", use_container_width=True):
            annual_effective_hours = float(st.session_state.get(f"{key_prefix}_annual_effective_hours", annual_effective_hours))
            trace.setdefault("base_data", {})
            trace["base_data"]["calculation_variables"] = {
                "region_id": region_id,
                "procurement_type": procurement_type,
                "annual_effective_hours": annual_effective_hours,
                "net_sale_price": net_sale_price,
                "shifts_per_day": st.session_state.get(f"{key_prefix}_shifts_per_day", default_shifts),
                "hours_per_shift": st.session_state.get(f"{key_prefix}_hours_per_shift", default_hours),
                "days_per_week": st.session_state.get(f"{key_prefix}_days_per_week", default_days),
                "extra_shift_per_week": st.session_state.get(f"{key_prefix}_extra_shift_per_week", default_extra),
                "weeks_per_year": st.session_state.get(f"{key_prefix}_weeks_per_year", default_weeks),
            }
            trace["base_data"]["production"] = {
                "qualified_annual_demand": qualified_annual_demand,
                "annual_other_demand": annual_other_demand,
                "manufacturing_batch_no": batch_no,
                "part_lifecycle_years": lifecycle_years,
                "production_start_date": str(prod_date),
            }
            ok_sv, resp_sv = _save_cost_trace(row, trace, {"calculation_name": calc_name, "currency_id": currency_id, "unit_id": unit_id})
            if ok_sv:
                st.success("基础数据已保存。")
                _clear_cache()
                st.rerun()
            st.error(resp_sv)

    with tabs[1]:
        comps = trace.get("components", {}) if isinstance(trace, dict) else {}
        material_rows = trace.get("material_rows", []) if isinstance(trace, dict) else []
        material_inputs = trace.get("material_inputs", {}) if isinstance(trace, dict) else {}

        t1, t2 = st.columns([0.82, 0.18])
        t1.markdown("#### 材料成本")
        edit_material = t2.button("编辑材料成本", key=f"{key_prefix}_edit_material", use_container_width=True, type="primary")

        if material_rows:
            table_rows: list[dict[str, Any]] = []
            for x in material_rows:
                row_name = x.get("name") or x.get("child_part_name") or x.get("part_name") or "-"
                row_code = x.get("code") or x.get("child_part_code") or x.get("part_code") or "-"
                table_rows.append(
                    {
                        "名称": row_name,
                        "编号": row_code,
                        "质量": x.get("effective_weight") or x.get("quantity"),
                        "质量单位": unit,
                        "单位价格": x.get("material_unit_price") or x.get("unit_price"),
                        "投入材料成本": x.get("input_material_cost"),
                        "废料名称": f"{row_name}的废料" if row_name != "-" else "-",
                        "废料重量": x.get("scrap_weight"),
                        "废料价格(-为收入/+为支出)": x.get("scrap_process_cost"),
                        "直接材料成本": x.get("standard_material_cost"),
                        "价格单位": ccy,
                    }
                )
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
        else:
            st.info("暂无材料成本明细，点击右上角“编辑材料成本”开始计算。")

        direct_material = float(comps.get("standard_material_total") or 0)
        st.markdown(
            f"<div class='field-card'><div class='field-k'>合计</div><div class='field-v'>直接材料成本 {direct_material:.2f} {ccy}/{unit}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("##### 材料其他成本：")
        material_scrap_cost = st.number_input(
            "材料报废成本",
            min_value=0.0,
            value=float(material_inputs.get("material_scrap_cost", comps.get("material_scrap_cost", 0)) or 0),
            step=0.1,
            key=f"{key_prefix}_mat_other_scrap",
        )
        indirect_material_cost = st.number_input(
            "材料间接费用",
            min_value=0.0,
            value=float(material_inputs.get("indirect_material_cost", comps.get("indirect_material_cost", 0)) or 0),
            step=0.1,
            key=f"{key_prefix}_mat_other_indirect",
        )
        material_inventory_interest = st.number_input(
            "材料库存利息",
            min_value=0.0,
            value=float(material_inputs.get("material_inventory_interest", comps.get("material_inventory_interest", 0)) or 0),
            step=0.1,
            key=f"{key_prefix}_mat_other_interest",
        )

        s1, s2 = st.columns([0.25, 0.75])
        save_mat_other = s1.button("保存材料其他成本", key=f"{key_prefix}_save_mat_other", use_container_width=True)

        if save_mat_other:
            theo = float(material_inputs.get("theoretical_feed_weight", 0) or 0)
            loss = float(material_inputs.get("feed_loss_rate", 0) or 0)
            net = float(material_inputs.get("net_weight", 0) or 0)
            unit_price = float(material_inputs.get("material_unit_price", 0) or 0)
            waste_income = float(material_inputs.get("waste_income_price", 0) or 0)
            waste_expense = float(material_inputs.get("waste_expense_price", 0) or 0)
            payload = {
                "calculation_name": row.get("calculation_name"),
                "currency_id": row.get("currency_id"),
                "unit_id": row.get("unit_id"),
                "theoretical_feed_weight": theo,
                "feed_loss_rate": loss,
                "net_weight": net,
                "material_unit_price": unit_price,
                "waste_income_price": waste_income,
                "waste_expense_price": waste_expense,
                "material_scrap_cost": float(material_scrap_cost),
                "indirect_material_cost": float(indirect_material_cost),
                "material_inventory_interest": float(material_inventory_interest),
                "remark": "更新材料成本",
            }
            ok_calc, resp_calc = _request("POST", f"/api/v1/cost-items/part/{part_id}/calculate", payload)
            if ok_calc:
                st.session_state.part_cost_item_id = resp_calc.get("id")
                _clear_cache()
                st.success("材料其他成本已保存。")
                st.rerun()
            st.error(resp_calc)

        material_total = direct_material + material_scrap_cost + indirect_material_cost + material_inventory_interest
        st.markdown(
            f"<div class='hero' style='margin-top:10px; margin-bottom:8px;'><h1 style='font-size:1.15rem !important;'>总计</h1><p style='font-size:1.4rem; font-family: IBM Plex Mono, monospace; color:#111827;'>材料成本 {material_total:.2f} {ccy}/{unit}</p></div>",
            unsafe_allow_html=True,
        )
        if edit_material:
            @st.dialog("材料计算器", width="large")
            def _dlg_material_calc() -> None:
                first_row = material_rows[0] if material_rows else {}
                default_material_name = first_row.get("name") or first_row.get("child_part_name") or first_row.get("part_name") or ""
                default_material_code = first_row.get("code") or first_row.get("child_part_code") or first_row.get("part_code") or ""

                st.markdown("### 基本信息")
                b1, b2 = st.columns(2)
                material_name = b1.text_input("材料名称", value=default_material_name, key=f"{key_prefix}_dlg_mat_name")
                material_code = b2.text_input("材料编号", value=default_material_code, key=f"{key_prefix}_dlg_mat_code")

                m_ok, materials_data = _load_rows("/api/v1/materials")
                material_options = ["-- 请选择 --"]
                material_map: dict[str, dict[str, Any]] = {}
                if m_ok and materials_data:
                    for m_item in materials_data:
                        lbl = f"{m_item.get('material_name') or '-'} | {m_item.get('material_code') or '-'}"
                        material_options.append(lbl)
                        material_map[lbl] = m_item
                selected_material = b1.selectbox("物质名称", material_options, key=f"{key_prefix}_dlg_material_ref")
                density = b2.number_input("密度", min_value=0.0, value=float(material_inputs.get("density", 0.0) or 0.0), step=0.0001, key=f"{key_prefix}_dlg_density")

                u_opts = [x for x in _fk_options("units") if x[0] is not None]
                u_labels = [x[1] for x in u_opts] or ["克"]
                quality_unit_label = b1.selectbox("质量单位", u_labels, index=0, key=f"{key_prefix}_dlg_quality_unit")
                quantity_unit_label = b1.selectbox("数量单位", u_labels, index=0, key=f"{key_prefix}_dlg_qty_unit")

                c_opts = [x for x in _fk_options("currencies") if x[0] is not None]
                c_labels = [x[1] for x in c_opts] or [ccy or "人民币"]
                currency_label = b2.selectbox("货币单位", c_labels, index=0, key=f"{key_prefix}_dlg_ccy")

                st.markdown("### 标准材料成本计算")
                st.markdown("#### 有效配重计算")
                w1, w2, w3 = st.columns(3)
                theoretical_feed_weight = w1.number_input("理论投料重量(克)", min_value=0.0, value=float(material_inputs.get("theoretical_feed_weight", 0) or 0), step=0.1, key=f"{key_prefix}_dlg_theoretical_feed_weight")
                feed_loss_rate = w2.number_input("投料损失(%)", min_value=0.0, value=float(material_inputs.get("feed_loss_rate", 0) or 0), step=0.1, key=f"{key_prefix}_dlg_feed_loss_rate")
                effective_weight = theoretical_feed_weight * (1.0 + feed_loss_rate / 100.0)
                w3.number_input("有效配重(克)", value=float(effective_weight), disabled=True, key=f"{key_prefix}_dlg_effective_weight")

                st.markdown("#### 材料成本计算")
                c1a, c2a, c3a = st.columns(3)
                net_weight = c1a.number_input("净重(克)", min_value=0.0, value=float(material_inputs.get("net_weight", 0) or 0), step=0.1, key=f"{key_prefix}_dlg_net_weight")
                material_unit_price = c2a.number_input("材料单位基价", min_value=0.0, value=float(material_inputs.get("material_unit_price", 0) or 0), step=0.0001, key=f"{key_prefix}_dlg_material_unit_price")
                input_material_cost = effective_weight * material_unit_price
                c3a.number_input("投入材料成本", value=float(input_material_cost), disabled=True, key=f"{key_prefix}_dlg_input_material_cost")

                st.markdown("#### 废料成本计算")
                s1a, s2a, s3a = st.columns(3)
                scrap_weight = effective_weight - net_weight
                scrap_rate = (scrap_weight / effective_weight * 100.0) if effective_weight > 0 else 0.0
                s1a.number_input("废料重量(克)", value=float(scrap_weight), disabled=True, key=f"{key_prefix}_dlg_scrap_weight")
                s1a.number_input("报废率(%)", value=float(scrap_rate), disabled=True, key=f"{key_prefix}_dlg_scrap_rate")
                waste_income_price = s2a.number_input("废料收入(CNY/克)", min_value=0.0, value=float(material_inputs.get("waste_income_price", 0) or 0), step=0.0001, key=f"{key_prefix}_dlg_waste_income_price")
                waste_expense_price = s2a.number_input("废料支出(CNY/克)", min_value=0.0, value=float(material_inputs.get("waste_expense_price", 0) or 0), step=0.0001, key=f"{key_prefix}_dlg_waste_expense_price")
                scrap_process_cost = scrap_weight * (waste_expense_price - waste_income_price)
                s3a.number_input("处理废料费用", value=float(scrap_process_cost), disabled=True, key=f"{key_prefix}_dlg_scrap_process_cost")

                standard_material_total = input_material_cost + scrap_process_cost
                st.markdown(f"<div class='field-card'><div class='field-k'>标准材料成本总计</div><div class='field-v'>{standard_material_total:.4f} {currency_label}/{quality_unit_label}</div></div>", unsafe_allow_html=True)

                x1, x2 = st.columns(2)
                if x1.button("取消", key=f"{key_prefix}_dlg_material_cancel", use_container_width=True):
                    st.rerun()

                if x2.button("确定", type="primary", key=f"{key_prefix}_dlg_material_ok", use_container_width=True):
                    if selected_material in material_map:
                        m_obj = material_map[selected_material]
                        material_name = m_obj.get("material_name") or material_name
                        material_code = m_obj.get("material_code") or material_code
                        density = m_obj.get("density") or density

                    payload = {
                        "calculation_name": row.get("calculation_name"),
                        "currency_id": row.get("currency_id"),
                        "unit_id": row.get("unit_id"),
                        "theoretical_feed_weight": theoretical_feed_weight,
                        "feed_loss_rate": feed_loss_rate,
                        "net_weight": net_weight,
                        "material_unit_price": material_unit_price,
                        "waste_income_price": waste_income_price,
                        "waste_expense_price": waste_expense_price,
                        "material_scrap_cost": material_scrap_cost,
                        "indirect_material_cost": indirect_material_cost,
                        "material_inventory_interest": material_inventory_interest,
                        "remark": "通过材料计算器重算",
                    }
                    ok_calc, resp_calc = _request("POST", f"/api/v1/cost-items/part/{part_id}/calculate", payload)
                    if not ok_calc:
                        st.error(resp_calc)
                        return

                    calc_id = resp_calc.get("id")
                    ok_new, row_new = _request("GET", f"/api/v1/cost-items/{calc_id}")
                    if ok_new:
                        tr = _parse_cost_trace(row_new)
                        tr.setdefault("material_meta", {})
                        tr["material_meta"].update({
                            "material_name": material_name,
                            "material_code": material_code,
                            "density": density,
                            "quality_unit_label": quality_unit_label,
                            "quantity_unit_label": quantity_unit_label,
                            "currency_label": currency_label,
                        })
                        _save_cost_trace(row_new, tr)

                    st.session_state.part_cost_item_id = calc_id
                    _clear_cache()
                    st.success("材料成本计算完成。")
                    st.rerun()

            _dlg_material_calc()

    with tabs[2]:
        trace.setdefault("manufacturing", {})
        mfg = trace.get("manufacturing", {})
        routes: list[dict[str, Any]] = mfg.get("routes", [])

        c1m, c2m = st.columns([0.15, 0.85])
        add_route = c1m.button("新增制造成本", key=f"{key_prefix}_mfg_add", type="primary", use_container_width=True)
        c2m.markdown(f"**{ccy}/{unit}**")

        if add_route:
            @st.dialog("新增制造成本", width="large")
            def _dlg_add_mfg_route() -> None:
                st.markdown("### 工艺参数")
                process_name = st.text_input("工序名称", key=f"{key_prefix}_mfg_process_name")

                p1, p2, p3 = st.columns(3)
                process_time_sec = p1.number_input("每件加工时间(秒/件)", min_value=0.0, value=0.0, step=0.1, key=f"{key_prefix}_mfg_process_time")
                pieces_per_batch = p1.number_input("每批来料数量(件)", min_value=0.0, value=0.0, step=1.0, key=f"{key_prefix}_mfg_batch_qty")
                scrap_setup_rate = p2.number_input("工艺报废和调机报废(%)", min_value=0.0, value=0.0, step=0.1, key=f"{key_prefix}_mfg_scrap_setup")
                batch_ratio = p2.number_input("生产批次比例(%)", min_value=0.0, value=100.0, step=0.1, key=f"{key_prefix}_mfg_batch_ratio")
                theoretical_capacity = p3.number_input("理论产能(件/小时)", min_value=0.0, value=0.0, step=0.1, key=f"{key_prefix}_mfg_theory_cap")
                effective_capacity = p3.number_input("有效产能(件/小时)", min_value=0.0, value=0.0, step=0.1, key=f"{key_prefix}_mfg_effective_cap")
                qualified_capacity = p3.number_input("合格品产能(件)", min_value=0.0, value=0.0, step=1.0, key=f"{key_prefix}_mfg_qualified_cap")
                system_utilization = p3.number_input("生产系统占用率(%)", min_value=0.0, value=0.0, step=0.1, key=f"{key_prefix}_mfg_utilization")
                current_batch_output = p3.number_input("当前工序每批生产数(件)", min_value=0.0, value=0.0, step=1.0, key=f"{key_prefix}_mfg_current_batch_output")

                st.markdown("### 直接设备成本")
                e1, e2, e3 = st.columns(3)
                equipment_model = e1.text_input("设备型号", key=f"{key_prefix}_mfg_eq_model")
                equipment_name = e1.text_input("设备名称", key=f"{key_prefix}_mfg_eq_name")
                manufacturer = e1.text_input("制造商", key=f"{key_prefix}_mfg_eq_manu")
                quantity = e2.number_input("数量", min_value=0.0, value=1.0, step=1.0, key=f"{key_prefix}_mfg_eq_qty")
                equipment_investment = e2.number_input("设备投资(CNY)", min_value=0.0, value=0.0, step=1000.0, key=f"{key_prefix}_mfg_eq_invest")
                equipment_rate_hour = e2.number_input("设备费率(CNY/小时)", min_value=0.0, value=0.0, step=0.1, key=f"{key_prefix}_mfg_eq_rate")

                total_rate_hour = equipment_rate_hour * quantity
                equipment_cost_piece = total_rate_hour * (process_time_sec / 3600.0) if process_time_sec > 0 else 0.0
                e3.number_input("设备总费率(CNY/小时)", value=float(total_rate_hour), disabled=True, key=f"{key_prefix}_mfg_eq_total_rate")
                e3.number_input("设备成本(CNY/件)", value=float(equipment_cost_piece), disabled=True, key=f"{key_prefix}_mfg_eq_piece_cost")
                e3.number_input("比例(%)", value=float(batch_ratio), disabled=True, key=f"{key_prefix}_mfg_eq_ratio")

                st.markdown("### 其他制造成本")
                o1, o2 = st.columns(2)
                direct_labor_cost = o1.number_input("直接人工成本", min_value=0.0, value=0.0, step=0.0001, key=f"{key_prefix}_mfg_direct_labor")
                mold_tooling_cost = o1.number_input("模具/工装分摊成本", min_value=0.0, value=0.0, step=0.0001, key=f"{key_prefix}_mfg_mold")
                setup_changeover_cost = o1.number_input("调机(换型)成本", min_value=0.0, value=0.0, step=0.0001, key=f"{key_prefix}_mfg_setup")
                remaining_indirect_cost = o1.number_input("剩余制造间接费用及工艺报废成本(制造成本II)", min_value=0.0, value=0.0, step=0.0001, key=f"{key_prefix}_mfg_indirect2")

                manufacturing_cost_i = equipment_cost_piece + direct_labor_cost + setup_changeover_cost
                manufacturing_cost_ii = mold_tooling_cost + remaining_indirect_cost
                manufacturing_total = manufacturing_cost_i + manufacturing_cost_ii
                o2.markdown(
                    f"""
                    <div class='field-card'><div class='field-k'>制造成本 I</div><div class='field-v'>{manufacturing_cost_i:.4f} {ccy}/{unit}</div></div>
                    <div class='field-card'><div class='field-k'>制造成本 II</div><div class='field-v'>{manufacturing_cost_ii:.4f} {ccy}/{unit}</div></div>
                    <div class='field-card'><div class='field-k'>制造总成本</div><div class='field-v'>{manufacturing_total:.4f} {ccy}/{unit}</div></div>
                    """,
                    unsafe_allow_html=True,
                )

                b1, b2 = st.columns(2)
                if b1.button("取消", key=f"{key_prefix}_mfg_cancel", use_container_width=True):
                    st.rerun()
                if b2.button("确定", type="primary", key=f"{key_prefix}_mfg_ok", use_container_width=True):
                    route = {
                        "process_name": process_name or f"工序{len(routes) + 1}",
                        "process_time_sec_per_piece": process_time_sec,
                        "pieces_per_batch": pieces_per_batch,
                        "scrap_and_setup_rate_pct": scrap_setup_rate,
                        "production_batch_ratio_pct": batch_ratio,
                        "theoretical_capacity_pph": theoretical_capacity,
                        "effective_capacity_pph": effective_capacity,
                        "qualified_capacity_piece": qualified_capacity,
                        "system_utilization_pct": system_utilization,
                        "current_batch_output_piece": current_batch_output,
                        "equipment": {
                            "model": equipment_model,
                            "name": equipment_name,
                            "manufacturer": manufacturer,
                            "quantity": quantity,
                            "investment_cny": equipment_investment,
                            "equipment_rate_cny_per_hour": equipment_rate_hour,
                            "total_rate_cny_per_hour": total_rate_hour,
                            "equipment_cost_cny_per_piece": equipment_cost_piece,
                            "ratio_pct": batch_ratio,
                        },
                        "direct_equipment_cost": equipment_cost_piece,
                        "direct_labor_cost": direct_labor_cost,
                        "setup_changeover_cost": setup_changeover_cost,
                        "mold_tooling_cost": mold_tooling_cost,
                        "remaining_indirect_cost_ii": remaining_indirect_cost,
                        "manufacturing_cost_i": manufacturing_cost_i,
                        "manufacturing_cost_ii": manufacturing_cost_ii,
                        "manufacturing_total": manufacturing_total,
                    }
                    routes.append(route)
                    trace["manufacturing"]["routes"] = routes

                    direct_equipment_sum = float(sum(float(x.get("direct_equipment_cost", 0) or 0) for x in routes))
                    direct_labor_sum = float(sum(float(x.get("direct_labor_cost", 0) or 0) for x in routes))
                    setup_sum = float(sum(float(x.get("setup_changeover_cost", 0) or 0) for x in routes))
                    mfg_i_sum = float(sum(float(x.get("manufacturing_cost_i", 0) or 0) for x in routes))
                    mfg_ii_sum = float(sum(float(x.get("manufacturing_cost_ii", 0) or 0) for x in routes))
                    mfg_total_sum = mfg_i_sum + mfg_ii_sum
                    trace["manufacturing"]["totals"] = {
                        "direct_equipment_cost": direct_equipment_sum,
                        "direct_labor_cost": direct_labor_sum,
                        "setup_changeover_cost": setup_sum,
                        "manufacturing_cost_i": mfg_i_sum,
                        "manufacturing_cost_ii": mfg_ii_sum,
                        "manufacturing_total": mfg_total_sum,
                    }

                    material_cost_now = float(row.get("material_cost") or 0)
                    overhead_cost_now = float(row.get("overhead_cost") or 0)
                    total_cost_now = material_cost_now + mfg_total_sum + overhead_cost_now
                    ok_mfg, resp_mfg = _save_cost_trace(
                        row,
                        trace,
                        {"manufacturing_cost": mfg_total_sum, "total_cost": total_cost_now, "remark": "新增制造成本明细"},
                    )
                    if ok_mfg:
                        _clear_cache()
                        st.success("制造成本已新增并写入。")
                        st.rerun()
                    st.error(resp_mfg)

            _dlg_add_mfg_route()

        if routes:
            show_rows: list[dict[str, Any]] = []
            for i, r in enumerate(routes):
                show_rows.append({"选取": False, "idx": i, "工序名称": r.get("process_name"), "直接设备成本": r.get("direct_equipment_cost"), "直接人工成本": r.get("direct_labor_cost"), "换型调机成本": r.get("setup_changeover_cost"), "平均每件的制造成本I": r.get("manufacturing_cost_i")})
            df_mfg = pd.DataFrame(show_rows)
            edited_mfg = st.data_editor(df_mfg, hide_index=True, use_container_width=True, disabled=[c for c in df_mfg.columns if c != "选取"], key=f"{key_prefix}_mfg_grid_{st.session_state.reload_token}")
            selected_mfg = edited_mfg[edited_mfg["选取"] == True]
            if not selected_mfg.empty:
                ridx = int(selected_mfg.iloc[0]["idx"])
                if st.button("删除选中工序", key=f"{key_prefix}_mfg_del", use_container_width=False):
                    if 0 <= ridx < len(routes):
                        routes.pop(ridx)
                        trace["manufacturing"]["routes"] = routes
                        direct_equipment_sum = float(sum(float(x.get("direct_equipment_cost", 0) or 0) for x in routes))
                        direct_labor_sum = float(sum(float(x.get("direct_labor_cost", 0) or 0) for x in routes))
                        setup_sum = float(sum(float(x.get("setup_changeover_cost", 0) or 0) for x in routes))
                        mfg_i_sum = float(sum(float(x.get("manufacturing_cost_i", 0) or 0) for x in routes))
                        mfg_ii_sum = float(sum(float(x.get("manufacturing_cost_ii", 0) or 0) for x in routes))
                        mfg_total_sum = mfg_i_sum + mfg_ii_sum
                        trace["manufacturing"]["totals"] = {"direct_equipment_cost": direct_equipment_sum, "direct_labor_cost": direct_labor_sum, "setup_changeover_cost": setup_sum, "manufacturing_cost_i": mfg_i_sum, "manufacturing_cost_ii": mfg_ii_sum, "manufacturing_total": mfg_total_sum}
                        material_cost_now = float(row.get("material_cost") or 0)
                        overhead_cost_now = float(row.get("overhead_cost") or 0)
                        total_cost_now = material_cost_now + mfg_total_sum + overhead_cost_now
                        ok_del, resp_del = _save_cost_trace(
                            row,
                            trace,
                            {"manufacturing_cost": mfg_total_sum, "total_cost": total_cost_now, "remark": "删除制造成本明细"},
                        )
                        if ok_del:
                            _clear_cache()
                            st.success("工序已删除。")
                            st.rerun()
                        st.error(resp_del)
        else:
            st.info("暂无制造成本工序，点击“新增制造成本”开始配置。")

        totals = trace.get("manufacturing", {}).get("totals", {})
        direct_equipment_sum = float(totals.get("direct_equipment_cost", 0) or 0)
        direct_labor_sum = float(totals.get("direct_labor_cost", 0) or 0)
        setup_sum = float(totals.get("setup_changeover_cost", 0) or 0)
        mfg_i_sum = float(totals.get("manufacturing_cost_i", 0) or 0)
        mfg_ii_sum = float(totals.get("manufacturing_cost_ii", 0) or 0)
        mfg_total_sum = float(totals.get("manufacturing_total", mfg_i_sum + mfg_ii_sum) or 0)

        st.markdown("### 合计")
        t1s, t2s, t3s = st.columns(3)
        t1s.number_input("直接设备成本", value=float(direct_equipment_sum), disabled=True, key=f"{key_prefix}_mfg_sum_eq")
        t2s.number_input("直接人工成本", value=float(direct_labor_sum), disabled=True, key=f"{key_prefix}_mfg_sum_labor")
        t3s.number_input("换型调机成本", value=float(setup_sum), disabled=True, key=f"{key_prefix}_mfg_sum_setup")
        st.markdown(f"<div class='field-card'><div class='field-k'>制造成本 I</div><div class='field-v'>{mfg_i_sum:.4f} {ccy}/{unit}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='field-card'><div class='field-k'>制造成本 II</div><div class='field-v'>{mfg_ii_sum:.4f} {ccy}/{unit}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero' style='margin-top:8px;'><h1 style='font-size:1.15rem !important;'>制造成本总计</h1><p style='font-size:1.4rem; font-family: IBM Plex Mono, monospace;'>{mfg_total_sum:.4f} {ccy}/{unit}</p></div>", unsafe_allow_html=True)

    with tabs[3]:
        comps = trace.get("components", {}) if isinstance(trace, dict) else {}
        overhead = trace.get("overhead", {}) if isinstance(trace, dict) else {}

        def _ov_value(key: str, fallback: float = 0.0) -> float:
            return float(overhead.get(key, comps.get(key, fallback)) or 0.0)

        def _ov_row(label: str, key: str) -> float:
            c1, c2, c3 = st.columns([0.48, 0.25, 0.27])
            c1.markdown(f"<div style='padding-top:6px'>{label}</div>", unsafe_allow_html=True)
            val = c2.number_input(label, min_value=0.0, value=_ov_value(key, 0.0), step=0.1, key=f"{key_prefix}_ov_{key}", label_visibility="collapsed")
            c3.markdown(f"<div style='padding-top:6px; color:#111827; font-family: IBM Plex Mono, monospace;'>{ccy_cn}/{unit_cn}</div>", unsafe_allow_html=True)
            return float(val)

        st.markdown("### 间接费用")

        st.markdown("#### 特殊直接成本")
        special_dev_alloc = _ov_row("零件特定开发分摊成本", "special_dev_alloc")
        special_launch_alloc = _ov_row("零件特定投产分摊成本", "special_launch_alloc")
        packaging_aux_alloc = _ov_row("包装/运输辅助材料分摊成本", "packaging_aux_alloc")

        st.markdown("#### 期间费用")
        sales_admin_cost = _ov_row("销售和一般管理成本", "sales_admin_cost")
        rnd_cost = _ov_row("研发成本", "rnd_cost")
        business_risk_cost = _ov_row("商业风险推算成本", "business_risk_cost")
        finished_goods_interest = _ov_row("库存成品的利息", "finished_goods_interest")
        other_after_prod = _ov_row("扣除生产成本后的其他支出", "other_after_prod")
        direct_mgmt_excl_prod = _ov_row("除生产成本外的直接管理费", "direct_mgmt_excl_prod")

        st.markdown("#### 利润")
        profit = _ov_row("利润", "profit")

        st.markdown("#### 账期及折扣")
        financing_discount = _ov_row("资金账期及折扣", "financing_discount")
        discount = _ov_row("折扣", "discount")

        st.markdown("#### 运费及关税")
        shipping_cost = _ov_row("运输成本", "shipping_cost")
        tariff = _ov_row("关税", "tariff")

        overhead_total = (
            special_dev_alloc + special_launch_alloc + packaging_aux_alloc
            + sales_admin_cost + rnd_cost + business_risk_cost + finished_goods_interest
            + other_after_prod + direct_mgmt_excl_prod
            + profit + financing_discount + discount + shipping_cost + tariff
        )

        st.markdown(
            f"<div class='field-card'><div class='field-k'>总计</div><div class='field-v'>间接费用 {overhead_total:.2f} {ccy_cn}/{unit_cn}</div></div>",
            unsafe_allow_html=True,
        )

        if st.button("保存间接费用", type="primary", key=f"{key_prefix}_save_overhead", use_container_width=True):
            ov_map = {
                "special_dev_alloc": special_dev_alloc,
                "special_launch_alloc": special_launch_alloc,
                "packaging_aux_alloc": packaging_aux_alloc,
                "sales_admin_cost": sales_admin_cost,
                "rnd_cost": rnd_cost,
                "business_risk_cost": business_risk_cost,
                "finished_goods_interest": finished_goods_interest,
                "other_after_prod": other_after_prod,
                "direct_mgmt_excl_prod": direct_mgmt_excl_prod,
                "profit": profit,
                "financing_discount": financing_discount,
                "discount": discount,
                "shipping_cost": shipping_cost,
                "tariff": tariff,
                "overhead_total": overhead_total,
            }
            trace.setdefault("overhead", {})
            trace["overhead"].update(ov_map)
            trace.setdefault("components", {})
            trace["components"].update(ov_map)

            material_cost_now = float(row.get("material_cost") or 0)
            manufacturing_cost_now = float(row.get("manufacturing_cost") or 0)
            total_cost_now = material_cost_now + manufacturing_cost_now + overhead_total

            ok_ov, resp_ov = _save_cost_trace(
                row,
                trace,
                {
                    "overhead_cost": overhead_total,
                    "total_cost": total_cost_now,
                    "remark": "保存间接费用",
                },
            )
            if ok_ov:
                _clear_cache()
                st.success("间接费用已保存。")
                st.rerun()
            st.error(resp_ov)

    with tabs[4]:
        st.markdown("#### 成本明细")
        comps = trace.get("components", {}) if isinstance(trace, dict) else {}
        mfg_totals = trace.get("manufacturing", {}).get("totals", {}) if isinstance(trace, dict) else {}
        overhead = trace.get("overhead", {}) if isinstance(trace, dict) else {}

        def _v(*vals: Any) -> float:
            for x in vals:
                if x is not None:
                    try:
                        return float(x)
                    except Exception:
                        continue
            return 0.0

        direct_equipment_cost = _v(mfg_totals.get("direct_equipment_cost"), comps.get("direct_equipment_cost"))
        setup_changeover_cost = _v(mfg_totals.get("setup_changeover_cost"), comps.get("setup_changeover_cost"))
        direct_labor_cost = _v(mfg_totals.get("direct_labor_cost"), comps.get("direct_labor_cost"))
        manufacturing_cost_i = _v(mfg_totals.get("manufacturing_cost_i"), comps.get("manufacturing_cost_i"))
        manufacturing_cost_ii = _v(mfg_totals.get("manufacturing_cost_ii"), comps.get("manufacturing_cost_ii"))

        special_direct_cost = _v(
            overhead.get("special_dev_alloc"), comps.get("special_dev_alloc")
        ) + _v(
            overhead.get("special_launch_alloc"), comps.get("special_launch_alloc")
        ) + _v(
            overhead.get("packaging_aux_alloc"), comps.get("packaging_aux_alloc")
        )
        period_cost = _v(
            overhead.get("sales_admin_cost"), comps.get("sales_admin_cost")
        ) + _v(
            overhead.get("rnd_cost"), comps.get("rnd_cost")
        ) + _v(
            overhead.get("business_risk_cost"), comps.get("business_risk_cost")
        ) + _v(
            overhead.get("finished_goods_interest"), comps.get("finished_goods_interest")
        ) + _v(
            overhead.get("other_after_prod"), comps.get("other_after_prod")
        ) + _v(
            overhead.get("direct_mgmt_excl_prod"), comps.get("direct_mgmt_excl_prod")
        )
        profit_cost = _v(overhead.get("profit"), comps.get("profit"))
        account_discount_cost = _v(overhead.get("financing_discount"), comps.get("financing_discount")) + _v(overhead.get("discount"), comps.get("discount"))
        shipping_tax_cost = _v(overhead.get("shipping_cost"), comps.get("shipping_cost")) + _v(overhead.get("tariff"), comps.get("tariff"))

        detail_rows = [
            {"成本类型": "材料报废成本", "成本": _v(comps.get("material_scrap_cost"))},
            {"成本类型": "材料间接费用", "成本": _v(comps.get("indirect_material_cost"))},
            {"成本类型": "材料库存利息", "成本": _v(comps.get("material_inventory_interest"))},
            {"成本类型": "材料成本", "成本": _v(row.get("material_cost"))},
            {"成本类型": "设备成本", "成本": direct_equipment_cost},
            {"成本类型": "换型调机成本", "成本": setup_changeover_cost},
            {"成本类型": "直接人工成本", "成本": direct_labor_cost},
            {"成本类型": "制造成本 I", "成本": manufacturing_cost_i},
            {"成本类型": "制造成本 II", "成本": manufacturing_cost_ii},
            {"成本类型": "特殊直接成本", "成本": special_direct_cost},
            {"成本类型": "期间费用", "成本": period_cost},
            {"成本类型": "利润", "成本": profit_cost},
            {"成本类型": "账期及折扣", "成本": account_discount_cost},
            {"成本类型": "运费及关税", "成本": shipping_tax_cost},
            {"成本类型": "间接费用", "成本": _v(row.get("overhead_cost"))},
            {"成本类型": "总成本", "成本": _v(row.get("total_cost"))},
        ]
        detail_df = pd.DataFrame(detail_rows)
        detail_df["货币单位"] = ccy_cn
        detail_df["数量单位"] = unit_cn
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

    with tabs[5]:
        st.markdown("#### 结果分析")
        comps = trace.get("components", {}) if isinstance(trace, dict) else {}
        overhead = trace.get("overhead", {}) if isinstance(trace, dict) else {}

        def _f(v: Any) -> float:
            try:
                return float(v or 0)
            except Exception:
                return 0.0

        material_cost = _f(row.get("material_cost"))
        manufacturing_cost = _f(row.get("manufacturing_cost"))
        special_direct_cost = _f(overhead.get("special_dev_alloc", comps.get("special_dev_alloc"))) + _f(overhead.get("special_launch_alloc", comps.get("special_launch_alloc"))) + _f(overhead.get("packaging_aux_alloc", comps.get("packaging_aux_alloc")))
        period_cost = _f(overhead.get("sales_admin_cost", comps.get("sales_admin_cost"))) + _f(overhead.get("rnd_cost", comps.get("rnd_cost"))) + _f(overhead.get("business_risk_cost", comps.get("business_risk_cost"))) + _f(overhead.get("finished_goods_interest", comps.get("finished_goods_interest"))) + _f(overhead.get("other_after_prod", comps.get("other_after_prod"))) + _f(overhead.get("direct_mgmt_excl_prod", comps.get("direct_mgmt_excl_prod")))
        profit_cost = _f(overhead.get("profit", comps.get("profit")))
        account_discount = _f(overhead.get("financing_discount", comps.get("financing_discount"))) + _f(overhead.get("discount", comps.get("discount")))
        shipping_tax = _f(overhead.get("shipping_cost", comps.get("shipping_cost"))) + _f(overhead.get("tariff", comps.get("tariff")))

        pie_items = [
            ("材料成本", material_cost),
            ("制造成本", manufacturing_cost),
            ("特殊直接成本", special_direct_cost),
            ("期间费用", period_cost),
            ("利润", profit_cost),
            ("账期及折扣", account_discount),
            ("运费及税费", shipping_tax),
        ]
        pie_items = [(k, v) for k, v in pie_items if v > 0]

        total_per_piece = _f(row.get("total_cost"))
        st.markdown(
            f"<div class='hero'><h1 style='font-size:1.2rem !important;'>总成本 {total_per_piece:.2f} {ccy_cn}/{unit_cn}</h1><p>总成本分布</p></div>",
            unsafe_allow_html=True,
        )

        if pie_items:
            font_prop = None
            for font_path in [
                r"C:\Windows\Fonts\msyh.ttc",
                r"C:\Windows\Fonts\simhei.ttf",
                r"C:\Windows\Fonts\simsun.ttc",
            ]:
                if os.path.exists(font_path):
                    font_prop = fm.FontProperties(fname=font_path)
                    break

            vals = [x[1] for x in pie_items]
            labels = [x[0] for x in pie_items]
            total_val = sum(vals) if vals else 0.0

            def _autopct(pct: float) -> str:
                return f"{pct:.1f}%" if pct >= 4 else ""

            fig, ax = plt.subplots(figsize=(11.5, 6.2))
            wedges, _, autotexts = ax.pie(
                vals,
                labels=None,
                autopct=_autopct,
                startangle=95,
                pctdistance=0.72,
                wedgeprops={"edgecolor": "white", "linewidth": 1},
            )
            ax.axis("equal")

            legend_labels = []
            for i, name in enumerate(labels):
                pct = (vals[i] / total_val * 100) if total_val else 0.0
                legend_labels.append(f"{name}  {vals[i]:.2f} ({pct:.1f}%)")

            if font_prop is not None:
                for txt in autotexts:
                    txt.set_fontproperties(font_prop)
                ax.legend(
                    wedges,
                    legend_labels,
                    loc="center left",
                    bbox_to_anchor=(1.02, 0.5),
                    frameon=False,
                    prop=font_prop,
                    labelspacing=1.0,
                )
            else:
                plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "Noto Sans CJK SC", "DejaVu Sans"]
                plt.rcParams["axes.unicode_minus"] = False
                ax.legend(
                    wedges,
                    legend_labels,
                    loc="center left",
                    bbox_to_anchor=(1.02, 0.5),
                    frameon=False,
                    labelspacing=1.0,
                )

            fig.subplots_adjust(left=0.04, right=0.72, top=0.95, bottom=0.06)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("暂无可分析的数据。")


def _render_part_material_cost_manage() -> None:
    st.info("材料成本明细独立页开发中")


def _render_home_dashboard() -> None:
    st.markdown(
        """
        <style>
        .home-hero {
          background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 55%, #0b4b8f 100%);
          border: 1px solid #1e293b;
          color: #e2e8f0;
          border-radius: 10px;
          padding: 22px 24px;
          margin-bottom: 16px;
          box-shadow: 0 8px 18px rgba(15, 23, 42, .22);
        }
        .home-hero h2 { margin: 0; font-size: 1.65rem; font-weight: 700; letter-spacing: .01em; }
        .home-hero p { margin: 8px 0 0 0; color: #cbd5e1; font-size: .95rem; line-height: 1.5; }
        .home-kpi { background:#fff; border:1px solid #d1d5db; border-top:3px solid #005abb; border-radius:6px; padding:12px 14px; min-height:94px; }
        .home-kpi-k { font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; color:#6b7280; font-weight:700; }
        .home-kpi-v { margin-top:6px; font-size:1.55rem; color:#111827; font-family:'IBM Plex Mono', monospace; font-weight:600; }
        .home-kpi-s { margin-top:6px; color:#4b5563; font-size:.84rem; }
        .home-panel { background:#fff; border:1px solid #d1d5db; border-radius:6px; padding:14px 14px 10px 14px; min-height:210px; }
        .home-panel h4 { margin:0 0 10px 0; color:#0f172a; font-size:1rem; font-weight:700; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="home-hero">
          <h2>🏭 零件成本管理系统工作台</h2>
          <p>面向工业制造场景的一体化主数据与成本决策中心，提供数据配置、BOM层级、成本计算与元数据地图等关键能力。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data_module_keys = [k for k, v in MODULES.items() if v["group"] != "零件管理"]
    part_module_keys = [k for k, v in MODULES.items() if v["group"] == "零件管理"]

    def _count_rows(module_key: str) -> int:
        ok, rows = _load_rows(MODULES[module_key]["endpoint"])
        if not ok or rows is None:
            return 0
        return len(rows)

    key_modules = ["parts", "bom", "bom_items", "cost_items", "material_types", "materials", "equipment", "currencies"]
    counts: dict[str, int] = {}
    for mk in key_modules:
        if mk in MODULES:
            counts[mk] = _count_rows(mk)

    total_records = 0
    for mk in MODULES.keys():
        total_records += _count_rows(mk)

    part_count = counts.get("parts", 0)
    bom_count = counts.get("boms", 0)
    cost_count = counts.get("cost_items", 0)
    attach_count = _count_rows("part_attachments") if "part_attachments" in MODULES else 0
    health_ok = _backend_ok(_base_url())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"<div class='home-kpi'><div class='home-kpi-k'>系统总记录</div><div class='home-kpi-v'>{total_records}</div><div class='home-kpi-s'>所有业务表对象总量</div></div>",
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"<div class='home-kpi'><div class='home-kpi-k'>零件主数据</div><div class='home-kpi-v'>{part_count}</div><div class='home-kpi-s'>Part 核心业务对象</div></div>",
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"<div class='home-kpi'><div class='home-kpi-k'>BOM 结构</div><div class='home-kpi-v'>{bom_count}</div><div class='home-kpi-s'>装配清单/层级关系</div></div>",
            unsafe_allow_html=True,
        )
    with k4:
        health_text = "正常" if health_ok else "异常"
        health_color = "#16a34a" if health_ok else "#dc2626"
        st.markdown(
            f"<div class='home-kpi'><div class='home-kpi-k'>后端健康状态</div><div class='home-kpi-v' style='color:{health_color}'>{health_text}</div><div class='home-kpi-s'>{_base_url()}</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    p1, p2 = st.columns([0.62, 0.38], gap="medium")
    with p1:
        st.markdown("<div class='home-panel'><h4>📊 业务模块数据规模概览</h4></div>", unsafe_allow_html=True)
        size_rows = []
        for mk in MODULES.keys():
            size_rows.append({"模块": MODULES[mk]["name"], "分组": MODULES[mk]["group"], "记录数": _count_rows(mk)})
        df_size = pd.DataFrame(size_rows).sort_values(by="记录数", ascending=False).head(12)
        st.bar_chart(df_size.set_index("模块")["记录数"], use_container_width=True)
        st.dataframe(df_size, use_container_width=True, hide_index=True)

    with p2:
        st.markdown("<div class='home-panel'><h4>🧭 运营管控与快捷入口</h4></div>", unsafe_allow_html=True)
        st.metric("成本计算记录", cost_count)
        st.metric("BOM子项明细", counts.get("bom_items", 0))
        st.metric("附件资料", attach_count)

        qa, qb = st.columns(2)
        if qa.button("进入数据配置", use_container_width=True):
            st.session_state.page_key = "overview_data"
            st.rerun()
        if qb.button("进入零件管理", use_container_width=True):
            st.session_state.page_key = "overview_parts"
            st.rerun()
        qc, qd = st.columns(2)
        if qc.button("元数据与数据地图", use_container_width=True):
            st.session_state.page_key = "metadata_map"
            st.rerun()
        if qd.button("审计日志", use_container_width=True):
            st.session_state.page_key = "logs"
            st.rerun()

        st.caption("系统简介")
        st.markdown(
            "\n".join(
                [
                    "1. 主数据治理：单位/币种/区域/设备/物质等统一维护",
                    "2. 业务对象治理：Part 与 BOM 形成零件结构唯一数据源",
                    "3. 报告数据服务：材料/制造/间接费用分解与结果分析",
                ]
            )
        )

    st.write("")
    c_left, c_right = st.columns([0.5, 0.5], gap="medium")
    with c_left:
        st.markdown("#### 📌 领域视角速览")
        view_mode = st.radio(
            "工作台视角",
            ["数据配置", "零件管理", "元数据", "审计日志"],
            horizontal=True,
            key="home_view_mode",
        )
        if view_mode == "数据配置":
            st.info(f"已接入 {len(data_module_keys)} 个数据配置模块，覆盖基础主数据与成本参数字典。")
        elif view_mode == "零件管理":
            st.info(f"零件运营对象：Part={part_count}，BOM={bom_count}，CostItem={cost_count}。")
        elif view_mode == "元数据":
            st.info("元数据地图可提供表结构、字段语义与主外键关系浏览。")
        else:
            st.info(f"会话期内审计日志条数：{len(st.session_state.logs)}")

    with c_right:
        st.markdown("#### ⏱️ 实时监控")
        t1, t2, t3 = st.columns(3)
        t1.markdown(
            f"<div class='stat-box'><div class='stat-k'>当前时间</div><div class='stat-v'>{datetime.now().strftime('%H:%M:%S')}</div></div>",
            unsafe_allow_html=True,
        )
        t2.markdown(
            f"<div class='stat-box'><div class='stat-k'>数据配置模块</div><div class='stat-v'>{len(data_module_keys)}</div></div>",
            unsafe_allow_html=True,
        )
        t3.markdown(
            f"<div class='stat-box'><div class='stat-k'>零件模块</div><div class='stat-v'>{len(part_module_keys)}</div></div>",
            unsafe_allow_html=True,
        )

def _render_overview(mode: str) -> None:
    if mode == "overview_data":
        title = "数据配置 (Data Configuration)"
        desc = "统一管理企业级基础主数据、设备模型、工艺物质及成本核算参数的定义与维护工作台。"
        groups_to_show = [g for g in sorted({v["group"] for v in MODULES.values()}) if g != "零件管理"]
    else:
        title = "零件管理 (Part Management)"
        desc = "企业核心业务对象：零件台账、物料分类定义与生命周期维护工作台。"
        groups_to_show = ["零件管理"]

    st.markdown(
        f"""
        <div class="hero">
          <h1>{title}</h1>
          <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for grp in groups_to_show:
        st.markdown(f"<h4 style='color: #374151; padding-bottom: 6px; margin-top: 20px; font-size:1.1rem; border-bottom: 2px solid #d1d5db;'>{grp}</h4>", unsafe_allow_html=True)
        keys = [k for k, v in MODULES.items() if v["group"] == grp]
        for i in range(0, len(keys), 3):
            cols = st.columns(3, gap="medium")
            for j, k in enumerate(keys[i : i + 3]):
                cfg = MODULES[k]
                with cols[j]:
                    st.markdown(f"<div class='module-card'><h4>{cfg['name']}</h4><p>{cfg['description']}</p></div>", unsafe_allow_html=True)
                    if st.button("进入工作台 →", key=f"go_{k}", use_container_width=True):
                        st.session_state.page_key = k
                        st.session_state.search_text = ""
                        st.rerun()


def _render_logs() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>系统审计与日志 (Audit Logs)</h1>
          <p>记录当前会话周期内的所有 DML (数据操纵语言) 事务级操作痕迹。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    logs = st.session_state.logs
    c1, c2 = st.columns([0.8, 0.2])
    if c2.button("清空本地审计表", use_container_width=True):
        st.session_state.logs = []
        st.rerun()
    if not logs:
        st.info("当前会话暂无事务记录。")
        return
    st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)


@st.cache_data(show_spinner=False)
def _load_metadata_dictionary() -> dict[str, Any]:
    p = os.path.join(os.path.dirname(__file__), "metadata_dictionary.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tables": []}


def _render_metadata_map() -> None:
    md = _load_metadata_dictionary()
    tables = md.get("tables", []) if isinstance(md, dict) else []

    st.markdown(
        """
        <div class="hero">
          <h1>元数据与数据地图 (Metadata & Data Map)</h1>
          <p>用于让系统数据“找得到、读得懂”，展示核心数据表结构、字段语义与主外键关系。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not tables:
        st.warning("元数据字典为空，请检查 metadata_dictionary.json")
        return

    q = st.text_input("检索表名/字段名/描述", placeholder="例如：part / bom / total_cost")

    table_rows: list[dict[str, Any]] = []
    for t in tables:
        table_rows.append(
            {
                "表名": t.get("table_name"),
                "显示名称": t.get("table_display_name"),
                "说明": t.get("table_description"),
                "字段数": len(t.get("fields", []) or []),
            }
        )

    if q.strip():
        ql = q.strip().lower()
        filtered = []
        for t in tables:
            blob = " ".join(
                [
                    str(t.get("table_name", "")),
                    str(t.get("table_display_name", "")),
                    str(t.get("table_description", "")),
                    " ".join(
                        [
                            f"{f.get('name','')} {f.get('description','')} {f.get('data_type','')} {f.get('references','') or ''}"
                            for f in (t.get("fields", []) or [])
                        ]
                    ),
                ]
            ).lower()
            if ql in blob:
                filtered.append(t)
        tables = filtered
        table_rows = [
            {
                "表名": t.get("table_name"),
                "显示名称": t.get("table_display_name"),
                "说明": t.get("table_description"),
                "字段数": len(t.get("fields", []) or []),
            }
            for t in tables
        ]

    st.markdown("#### 核心数据表")
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    if not tables:
        st.info("无匹配结果。")
        return

    st.markdown("#### 字段字典")
    options = [f"{t.get('table_name')} - {t.get('table_display_name')}" for t in tables]
    selected = st.selectbox("选择数据表", options, index=0)
    t = tables[options.index(selected)]

    rows = []
    for f in (t.get("fields", []) or []):
        rows.append(
            {
                "字段名": f.get("name"),
                "字段描述": f.get("description"),
                "数据类型": f.get("data_type"),
                "主键": "是" if f.get("is_primary_key") else "否",
                "外键": "是" if f.get("is_foreign_key") else "否",
                "引用": f.get("references") or "-",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.download_button(
        "下载元数据字典 JSON",
        json.dumps(md, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="metadata_dictionary.json",
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    _init_state()
    _autofix_api_base_url()

    st.sidebar.markdown(
        """
        <style>
        [data-testid="stSidebar"] div.stButton > button {
          width: 100% !important;
          min-height: 46px !important;
          font-size: 1.05rem !important;
          font-weight: 650 !important;
          border-radius: 8px !important;
          border: 1px solid #334155 !important;
          background: rgba(255,255,255,0.06) !important;
          color: #f8fafc !important;
          text-align: left !important;
          padding-left: 0.95rem !important;
          margin-bottom: 0.4rem !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover {
          border-color: #38bdf8 !important;
          background: rgba(56,189,248,0.18) !important;
          transform: translateY(-1px);
        }
        .side-brand {
          border: 1px solid #334155;
          background: linear-gradient(180deg, rgba(15,23,42,.96), rgba(30,41,59,.84));
          border-radius: 10px;
          padding: 13px 12px 11px 12px;
          margin-bottom: 11px;
        }
        .side-brand-title {
          font-size: 1.24rem;
          font-weight: 750;
          color: #e2e8f0;
          margin: 0;
          line-height: 1.2;
        }
        .side-brand-sub {
          color: #94a3b8;
          font-size: 0.84rem;
          margin-top: 6px;
        }
        .side-sec {
          color: #cbd5e1;
          font-size: 0.95rem;
          font-weight: 750;
          margin: 0.85rem 0 0.46rem 0.1rem;
          letter-spacing: .02em;
        }
        .side-info {
          border: 1px solid #334155;
          border-radius: 10px;
          background: rgba(15,23,42,.55);
          padding: 10px 12px;
          margin-top: 10px;
          color: #cbd5e1;
          font-size: .83rem;
          line-height: 1.58;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="side-brand">
          <div class="side-brand-title">🏭 零件成本管理系统</div>
          <div class="side-brand-sub">Part Cost Management System</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data_module_keys = [k for k, v in MODULES.items() if v["group"] != "零件管理"]
    part_module_keys = [k for k, v in MODULES.items() if v["group"] == "零件管理"]
    part_pages = {"overview_parts", "part_bom_detail", "part_cost_list", "part_cost_detail", "part_material_cost_manage"}

    if st.session_state.page_key in part_pages or st.session_state.page_key in part_module_keys:
        current_domain = "零件管理"
    elif st.session_state.page_key == "metadata_map":
        current_domain = "元数据"
    elif st.session_state.page_key == "logs":
        current_domain = "审计日志"
    elif st.session_state.page_key in {"overview_home"}:
        current_domain = "首页大盘"
    else:
        current_domain = "数据配置"

    st.sidebar.markdown("<div class='side-sec'>核心业务域</div>", unsafe_allow_html=True)
    if st.sidebar.button("🏠 首页工作台", key="nav_domain_home"):
        st.session_state.page_key = "overview_home"
        st.session_state.search_text = ""
        st.rerun()
    if st.sidebar.button("🗂 数据配置", key="nav_domain_data"):
        st.session_state.page_key = "overview_data"
        st.session_state.search_text = ""
        st.rerun()
    if st.sidebar.button("⚙ 零件管理", key="nav_domain_parts"):
        st.session_state.page_key = "overview_parts"
        st.session_state.search_text = ""
        st.rerun()
    if st.sidebar.button("🧭 元数据与数据地图", key="nav_domain_meta"):
        st.session_state.page_key = "metadata_map"
        st.session_state.search_text = ""
        st.rerun()
    if st.sidebar.button("📜 审计日志", key="nav_domain_logs"):
        st.session_state.page_key = "logs"
        st.session_state.search_text = ""
        st.rerun()

    st.sidebar.markdown("<div class='side-sec'>模块导航</div>", unsafe_allow_html=True)
    if current_domain == "首页大盘":
        st.sidebar.button("• 首页总览", key="sub_home_main", disabled=True)
        if st.sidebar.button("→ 快速进入数据配置", key="sub_home_to_data"):
            st.session_state.page_key = "overview_data"
            st.rerun()
        if st.sidebar.button("→ 快速进入零件管理", key="sub_home_to_parts"):
            st.session_state.page_key = "overview_parts"
            st.rerun()
    elif current_domain == "数据配置":
        if st.sidebar.button("• 数据配置总览", key="sub_data_overview"):
            st.session_state.page_key = "overview_data"
            st.session_state.search_text = ""
            st.rerun()
        for grp in sorted({MODULES[k]["group"] for k in data_module_keys}):
            with st.sidebar.expander(f"◈ {grp}", expanded=False):
                for k in [x for x in data_module_keys if MODULES[x]["group"] == grp]:
                    if st.button(f"· {MODULES[k]['name']}", key=f"sub_data_{k}", use_container_width=True):
                        st.session_state.page_key = k
                        st.session_state.search_text = ""
                        st.rerun()
    elif current_domain == "零件管理":
        if st.sidebar.button("• 零件管理总览", key="sub_parts_overview"):
            st.session_state.page_key = "overview_parts"
            st.session_state.search_text = ""
            st.rerun()
        for k in part_module_keys:
            if st.sidebar.button(f"· {MODULES[k]['name']}", key=f"sub_part_{k}"):
                st.session_state.page_key = k
                st.session_state.search_text = ""
                st.rerun()
        if st.sidebar.button("· BOM层级详情", key="sub_part_bom_detail"):
            st.session_state.page_key = "part_bom_detail"
            st.rerun()
        if st.sidebar.button("· 成本计算列表", key="sub_part_cost_list"):
            st.session_state.page_key = "part_cost_list"
            st.rerun()
    elif current_domain == "元数据":
        st.sidebar.button("• 元数据字典总览", key="sub_meta_main", disabled=True)
    else:
        st.sidebar.button("• 操作审计日志", key="sub_logs_main", disabled=True)

    st.sidebar.markdown(
        f"""
        <div class='side-info'>
          <div><b>当前域</b>：{current_domain}</div>
          <div><b>数据配置模块</b>：{len(data_module_keys)} 个</div>
          <div><b>零件管理模块</b>：{len(part_module_keys)} 个</div>
          <div style="word-break: break-all;"><b>当前页面键</b>：{st.session_state.page_key}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.page_key == "overview_home":
        _render_home_dashboard()
    elif st.session_state.page_key == "overview_data":
        _render_overview("overview_data")
    elif st.session_state.page_key == "overview_parts":
        _render_overview("overview_parts")
    elif st.session_state.page_key == "part_bom_detail":
        _render_part_bom_detail()
    elif st.session_state.page_key == "part_cost_list":
        _render_part_cost_list()
    elif st.session_state.page_key == "part_cost_detail":
        _render_part_cost_detail()
    elif st.session_state.page_key == "part_material_cost_manage":
        _render_part_material_cost_manage()
    elif st.session_state.page_key == "metadata_map":
        _render_metadata_map()
    elif st.session_state.page_key == "logs":
        _render_logs()
    else:
        _render_module(st.session_state.page_key)

if __name__ == "__main__":
    main()