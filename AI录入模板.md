# AI 助手数据录入模板

本文档用于配合系统右下角 AI 助手的“聊天框录入”能力。把下面任一模板复制到 AI 聊天框，按实际数据修改后发送即可。

## 使用规则

- 外层建议使用 `workflow_data`。
- 编码字段用于去重和关联，例如 `unit_code`、`currency_code`、`part_code`、`bom_code`。
- 已存在的编码会自动跳过，不会重复创建。
- 成本里的 `total_cost` 可不填，系统会按 `material_cost + manufacturing_cost + overhead_cost` 自动计算。
- BOM 明细通过 `bom_code` 关联 BOM，通过 `child_part_code` 关联子零件。

## 模板 1：基础配置最小模板

适合先录入单位、币种、物料类型、物质分类。

```json
{
  "workflow_data": {
    "units": [
      {
        "unit_code": "PCS",
        "unit_name": "件",
        "unit_category": "数量",
        "unit_factor": 1
      },
      {
        "unit_code": "KG",
        "unit_name": "千克",
        "unit_category": "质量",
        "unit_factor": 1
      }
    ],
    "currencies": [
      {
        "currency_code": "CNY",
        "currency_name": "人民币",
        "currency_symbol": "¥",
        "precision_scale": 2,
        "is_base_currency": true
      }
    ],
    "material_types": [
      {
        "material_type_code": "ASM",
        "material_type_name": "总成",
        "description": "装配类零件"
      },
      {
        "material_type_code": "COMP",
        "material_type_name": "组件",
        "description": "子组件或单体零件"
      }
    ],
    "material_categories": [
      {
        "category_code": "ELEC",
        "category_name": "电子件",
        "category_type": "SUBSTANCE"
      },
      {
        "category_code": "METAL",
        "category_name": "金属件",
        "category_type": "SUBSTANCE"
      }
    ]
  }
}
```

## 模板 2：物质与零件主数据模板

适合录入材料/物质，以及核心零件台账。

```json
{
  "workflow_data": {
    "units": [
      {
        "unit_code": "PCS",
        "unit_name": "件",
        "unit_category": "数量"
      },
      {
        "unit_code": "KG",
        "unit_name": "千克",
        "unit_category": "质量"
      }
    ],
    "material_categories": [
      {
        "category_code": "ELEC",
        "category_name": "电子件"
      }
    ],
    "materials": [
      {
        "material_code": "MAT-CU",
        "material_name": "铜材",
        "category_code": "ELEC",
        "density": 8.96,
        "density_unit_code": "KG",
        "default_quantity_unit_code": "KG",
        "specification": "通用铜材"
      }
    ],
    "material_types": [
      {
        "material_type_code": "ASM",
        "material_type_name": "总成"
      },
      {
        "material_type_code": "PCB",
        "material_type_name": "控制板"
      }
    ],
    "parts": [
      {
        "part_code": "PART-CTRL-ASM-001",
        "part_name": "工业控制模块总成",
        "part_description": "用于设备控制柜的控制模块",
        "part_type": "ASSEMBLY",
        "material_type_code": "ASM",
        "material_category_code": "ELEC",
        "quantity_unit_code": "PCS",
        "part_status": "DRAFT",
        "lifecycle_stage": "DESIGN",
        "revision_no": "A",
        "version_no": 1
      },
      {
        "part_code": "PART-PCB-001",
        "part_name": "主控 PCB 板",
        "part_description": "控制模块核心电路板",
        "part_type": "COMPONENT",
        "material_type_code": "PCB",
        "material_category_code": "ELEC",
        "preferred_material_code": "MAT-CU",
        "quantity_unit_code": "PCS",
        "part_status": "DRAFT",
        "lifecycle_stage": "DESIGN",
        "revision_no": "A"
      }
    ]
  }
}
```

## 模板 3：BOM 结构模板

适合已有零件后，单独录入 BOM 头和 BOM 明细。

```json
{
  "workflow_data": {
    "parts": [
      {
        "part_code": "PART-CTRL-ASM-001",
        "part_name": "工业控制模块总成",
        "part_type": "ASSEMBLY",
        "quantity_unit_code": "PCS"
      },
      {
        "part_code": "PART-PCB-001",
        "part_name": "主控 PCB 板",
        "part_type": "COMPONENT",
        "quantity_unit_code": "PCS"
      },
      {
        "part_code": "PART-HOUSING-001",
        "part_name": "模块外壳",
        "part_type": "COMPONENT",
        "quantity_unit_code": "PCS"
      }
    ],
    "boms": [
      {
        "bom_code": "BOM-PART-CTRL-ASM-001",
        "bom_name": "工业控制模块总成 BOM",
        "part_code": "PART-CTRL-ASM-001",
        "version_no": "V1",
        "status": "RELEASED"
      }
    ],
    "bom_items": [
      {
        "bom_code": "BOM-PART-CTRL-ASM-001",
        "child_part_code": "PART-PCB-001",
        "quantity": 1,
        "quantity_unit_code": "PCS",
        "sort_no": 1,
        "remark": "核心控制板"
      },
      {
        "bom_code": "BOM-PART-CTRL-ASM-001",
        "child_part_code": "PART-HOUSING-001",
        "quantity": 1,
        "quantity_unit_code": "PCS",
        "sort_no": 2,
        "remark": "外壳件"
      }
    ]
  }
}
```

## 模板 4：零件成本录入模板

适合只录入成本结果。若零件、币种、单位不存在，请先用前面的模板创建。

```json
{
  "workflow_data": {
    "cost_items": [
      {
        "calculation_name": "工业控制模块总成-标准成本",
        "part_code": "PART-CTRL-ASM-001",
        "currency_code": "CNY",
        "unit_code": "PCS",
        "material_cost": 128.5,
        "manufacturing_cost": 36.2,
        "overhead_cost": 18.8,
        "total_cost": 183.5,
        "rule_version": "ai_import_v1",
        "trace_detail": {
          "base_data": {
            "batch_size": 1000,
            "quote_version": "2026-Q2"
          },
          "material_cost": {
            "pcb": 82.5,
            "housing": 26,
            "fasteners": 20
          },
          "manufacturing_cost": {
            "assembly_minutes": 12,
            "labor_rate_per_minute": 2.4,
            "test_cost": 7.4
          },
          "overhead_cost": {
            "factory_overhead": 12.5,
            "quality_overhead": 6.3
          },
          "result_analysis": {
            "largest_cost_driver": "material_cost",
            "optimization_hint": "优先评估 PCB 板采购价格与替代供应商"
          }
        },
        "remark": "AI助手录入的标准成本"
      }
    ]
  }
}
```

## 模板 5：完整工作流模板

适合一次性录入完整链路：基础配置、物质、零件、BOM、成本。

```json
{
  "workflow_data": {
    "units": [
      {
        "unit_code": "PCS",
        "unit_name": "件",
        "unit_category": "数量"
      },
      {
        "unit_code": "KG",
        "unit_name": "千克",
        "unit_category": "质量"
      }
    ],
    "currencies": [
      {
        "currency_code": "CNY",
        "currency_name": "人民币",
        "currency_symbol": "¥",
        "is_base_currency": true
      }
    ],
    "material_types": [
      {
        "material_type_code": "ASM",
        "material_type_name": "总成"
      },
      {
        "material_type_code": "PCB",
        "material_type_name": "PCB 板"
      },
      {
        "material_type_code": "CASE",
        "material_type_name": "壳体"
      }
    ],
    "material_categories": [
      {
        "category_code": "ELEC",
        "category_name": "电子件"
      },
      {
        "category_code": "PLASTIC",
        "category_name": "塑料件"
      }
    ],
    "materials": [
      {
        "material_code": "MAT-CU",
        "material_name": "铜材",
        "category_code": "ELEC",
        "density": 8.96,
        "density_unit_code": "KG"
      },
      {
        "material_code": "MAT-ABS",
        "material_name": "ABS 塑料",
        "category_code": "PLASTIC",
        "density": 1.04,
        "density_unit_code": "KG"
      }
    ],
    "parts": [
      {
        "part_code": "PART-CTRL-ASM-002",
        "part_name": "智能控制模块总成",
        "part_description": "带通信接口的控制模块",
        "part_type": "ASSEMBLY",
        "material_type_code": "ASM",
        "material_category_code": "ELEC",
        "quantity_unit_code": "PCS",
        "part_status": "DRAFT",
        "lifecycle_stage": "DESIGN",
        "revision_no": "A"
      },
      {
        "part_code": "PART-PCB-002",
        "part_name": "通信 PCB 板",
        "part_type": "COMPONENT",
        "material_type_code": "PCB",
        "material_category_code": "ELEC",
        "preferred_material_code": "MAT-CU",
        "quantity_unit_code": "PCS"
      },
      {
        "part_code": "PART-CASE-002",
        "part_name": "控制模块塑料外壳",
        "part_type": "COMPONENT",
        "material_type_code": "CASE",
        "material_category_code": "PLASTIC",
        "preferred_material_code": "MAT-ABS",
        "quantity_unit_code": "PCS"
      }
    ],
    "boms": [
      {
        "bom_code": "BOM-PART-CTRL-ASM-002",
        "bom_name": "智能控制模块总成 BOM",
        "part_code": "PART-CTRL-ASM-002",
        "version_no": "V1",
        "status": "RELEASED"
      }
    ],
    "bom_items": [
      {
        "bom_code": "BOM-PART-CTRL-ASM-002",
        "child_part_code": "PART-PCB-002",
        "quantity": 1,
        "quantity_unit_code": "PCS",
        "sort_no": 1
      },
      {
        "bom_code": "BOM-PART-CTRL-ASM-002",
        "child_part_code": "PART-CASE-002",
        "quantity": 1,
        "quantity_unit_code": "PCS",
        "sort_no": 2
      }
    ],
    "cost_items": [
      {
        "calculation_name": "智能控制模块总成-目标成本",
        "part_code": "PART-CTRL-ASM-002",
        "currency_code": "CNY",
        "unit_code": "PCS",
        "material_cost": 156.8,
        "manufacturing_cost": 42.6,
        "overhead_cost": 20.4,
        "rule_version": "ai_import_v1",
        "trace_detail": {
          "base_data": {
            "annual_volume": 50000,
            "quote_batch": 1000
          },
          "cost_detail": [
            {
              "item": "PCB",
              "amount": 108.2
            },
            {
              "item": "塑料外壳",
              "amount": 31.6
            },
            {
              "item": "辅料与紧固件",
              "amount": 17.0
            },
            {
              "item": "装配与测试",
              "amount": 42.6
            },
            {
              "item": "间接费用",
              "amount": 20.4
            }
          ],
          "result_analysis": {
            "material_ratio": "约 71.34%",
            "manufacturing_ratio": "约 19.38%",
            "overhead_ratio": "约 9.28%",
            "recommendation": "材料成本占比最高，优先从 PCB 采购、外壳材料和辅料标准化入手。"
          }
        },
        "remark": "完整工作流模板示例"
      }
    ]
  }
}
```

## 模板 6：零件内嵌成本快捷模板

适合只想围绕零件快速带入成本。系统会把每个零件里的 `cost` 转成成本记录。

```json
{
  "workflow_data": {
    "units": [
      {
        "unit_code": "PCS",
        "unit_name": "件",
        "unit_category": "数量"
      }
    ],
    "currencies": [
      {
        "currency_code": "CNY",
        "currency_name": "人民币"
      }
    ],
    "parts": [
      {
        "part_code": "PART-SENSOR-001",
        "part_name": "温度传感器组件",
        "part_type": "COMPONENT",
        "quantity_unit_code": "PCS",
        "cost": {
          "calculation_name": "温度传感器组件-快速成本",
          "currency_code": "CNY",
          "unit_code": "PCS",
          "material_cost": 22.6,
          "manufacturing_cost": 8.4,
          "overhead_cost": 3.2,
          "remark": "零件内嵌成本快捷录入"
        }
      }
    ]
  }
}
```

## 常用字段速查

| 数据块 | 关键字段 | 说明 |
| --- | --- | --- |
| `units` | `unit_code`, `unit_name`, `unit_category` | 单位配置 |
| `currencies` | `currency_code`, `currency_name` | 币种配置 |
| `material_types` | `material_type_code`, `material_type_name` | 物料类型 |
| `material_categories` | `category_code`, `category_name` | 物质分类 |
| `materials` | `material_code`, `material_name`, `category_code` | 物质/材料 |
| `parts` | `part_code`, `part_name`, `quantity_unit_code` | 零件主数据 |
| `boms` | `bom_code`, `part_code` | BOM 头，`part_code` 是父零件 |
| `bom_items` | `bom_code`, `child_part_code`, `quantity` | BOM 明细 |
| `cost_items` | `calculation_name`, `part_code`, `currency_code` | 成本记录 |

