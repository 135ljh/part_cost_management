-- IDME 工业数据管理系统：MySQL 8.0 建表脚本

-- 目标：兼容先前低代码系统能力，并为新系统扩展预留较强泛化能力

SET NAMES utf8mb4;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `meta_column_definition`;

DROP TABLE IF EXISTS `meta_table_definition`;

DROP TABLE IF EXISTS `cost_trace`;

DROP TABLE IF EXISTS `cost_summary`;

DROP TABLE IF EXISTS `cost_component`;

DROP TABLE IF EXISTS `formula_definition`;

DROP TABLE IF EXISTS `process_equipment_usage`;

DROP TABLE IF EXISTS `process_operation`;

DROP TABLE IF EXISTS `cost_material_item`;

DROP TABLE IF EXISTS `cost_calculation`;

DROP TABLE IF EXISTS `equipment_cost_profile`;

DROP TABLE IF EXISTS `equipment_rate`;

DROP TABLE IF EXISTS `equipment_specification`;

DROP TABLE IF EXISTS `equipment`;

DROP TABLE IF EXISTS `equipment_category`;

DROP TABLE IF EXISTS `bom_item`;

DROP TABLE IF EXISTS `bom`;

DROP TABLE IF EXISTS `part_attachment`;

DROP TABLE IF EXISTS `part`;

DROP TABLE IF EXISTS `region_cost_profile`;

DROP TABLE IF EXISTS `material_price`;

DROP TABLE IF EXISTS `material`;

DROP TABLE IF EXISTS `material_category`;

DROP TABLE IF EXISTS `region`;

DROP TABLE IF EXISTS `unit`;

DROP TABLE IF EXISTS `currency_exchange_rate`;

DROP TABLE IF EXISTS `currency`;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `currency` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `currency_code` VARCHAR(16) UNIQUE NOT NULL COMMENT 'ISO 货币代码，如 CNY/USD',
  `currency_name` VARCHAR(64) NOT NULL COMMENT '货币名称',
  `currency_symbol` VARCHAR(16) COMMENT '货币符号',
  `precision_scale` INT NOT NULL DEFAULT 2 COMMENT '金额小数位数',
  `is_base_currency` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否系统基准货币',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_currency_code (currency_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='货币主数据，对应低代码 Currency，用于全系统统一币种和金额精度控制。';

CREATE TABLE `currency_exchange_rate` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `from_currency_id` BIGINT UNSIGNED NOT NULL COMMENT '源货币',
  `to_currency_id` BIGINT UNSIGNED NOT NULL COMMENT '目标货币',
  `rate_type` VARCHAR(32) NOT NULL COMMENT 'REALTIME/FIXED/MANUAL',
  `exchange_rate` DECIMAL(20,8) NOT NULL COMMENT '汇率值',
  `effective_date` DATETIME NOT NULL COMMENT '生效时间',
  `source_name` VARCHAR(128) COMMENT '数据来源',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_fx_pair_type_date (from_currency_id, to_currency_id, rate_type, effective_date),
  KEY idx_fx_to_currency (to_currency_id),
  CONSTRAINT `fk_currency_exchange_rate_from_currency_id` FOREIGN KEY (`from_currency_id`) REFERENCES `currency` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_currency_exchange_rate_to_currency_id` FOREIGN KEY (`to_currency_id`) REFERENCES `currency` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='汇率配置，对应低代码 CurrencyExchange。用货币对替代旧模型中的单一 ISO 字段，支持实时/固定/手工汇率。';

CREATE TABLE `unit` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `unit_code` VARCHAR(32) UNIQUE NOT NULL COMMENT '单位编码',
  `unit_name` VARCHAR(64) NOT NULL COMMENT '单位名称',
  `unit_display_name` VARCHAR(64) COMMENT '显示名称',
  `unit_category` VARCHAR(64) NOT NULL COMMENT '单位类别，如质量/体积/面积/时间',
  `measurement_system` VARCHAR(64) COMMENT '度量体系',
  `base_unit_id` BIGINT UNSIGNED COMMENT '所属基准单位',
  `unit_factor` DECIMAL(20,8) NOT NULL DEFAULT 1 COMMENT '相对基准单位的换算系数',
  `sync_time` DATETIME COMMENT '同步时间',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_unit_code (unit_code),
  KEY idx_unit_base_unit (base_unit_id),
  CONSTRAINT `fk_unit_base_unit_id` FOREIGN KEY (`base_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='计量单位主数据，对应低代码 Unit。支持单位类别、换算因子、基准单位自关联。';

CREATE TABLE `region` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `region_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '区域编码',
  `region_name` VARCHAR(128) NOT NULL COMMENT '区域名称',
  `region_type` VARCHAR(64) NOT NULL COMMENT '区域类型',
  `parent_id` BIGINT UNSIGNED COMMENT '上级区域',
  `level_no` INT NOT NULL DEFAULT 1 COMMENT '层级深度',
  `full_name` VARCHAR(512) COMMENT '全路径名称',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_region_code (region_code),
  KEY idx_region_parent (parent_id),
  CONSTRAINT `fk_region_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `region` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='区域主数据，对应低代码 Region，采用自关联树结构统一国家/省/市/区/街道/工厂地址层级。';

CREATE TABLE `material_category` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `category_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '分类编码',
  `category_name` VARCHAR(128) NOT NULL COMMENT '分类名称',
  `category_type` VARCHAR(32) NOT NULL DEFAULT 'MATERIAL' COMMENT '分类类型：MATERIAL/SUBSTANCE',
  `parent_id` BIGINT UNSIGNED COMMENT '父分类',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_material_category_code (category_code),
  KEY idx_material_category_parent (parent_id),
  CONSTRAINT `fk_material_category_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `material_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='统一的材料/物质分类树。用于吸收低代码 substanceClassfication 与 materialClassification 的重复概念。';

CREATE TABLE `material` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `material_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '材料编码',
  `material_name` VARCHAR(128) NOT NULL COMMENT '材料名称',
  `category_id` BIGINT UNSIGNED COMMENT '所属材料分类',
  `density` DECIMAL(20,8) COMMENT '密度',
  `density_unit_id` BIGINT UNSIGNED COMMENT '密度单位',
  `default_quantity_unit_id` BIGINT UNSIGNED COMMENT '默认数量单位',
  `scrap_material_id` BIGINT UNSIGNED COMMENT '默认废料物料',
  `specification` VARCHAR(255) COMMENT '规格说明',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_material_code (material_code),
  KEY idx_material_category (category_id),
  KEY idx_material_density_unit (density_unit_id),
  KEY idx_material_default_quantity_unit (default_quantity_unit_id),
  KEY idx_material_scrap_material (scrap_material_id),
  CONSTRAINT `fk_material_category_id` FOREIGN KEY (`category_id`) REFERENCES `material_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_material_density_unit_id` FOREIGN KEY (`density_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_material_default_quantity_unit_id` FOREIGN KEY (`default_quantity_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_material_scrap_material_id` FOREIGN KEY (`scrap_material_id`) REFERENCES `material` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='材料/物质主数据，对应低代码 substance，并为成本计算提供标准物料主数据。';

CREATE TABLE `material_price` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `material_id` BIGINT UNSIGNED NOT NULL COMMENT '材料',
  `region_id` BIGINT UNSIGNED COMMENT '适用区域',
  `supplier_name` VARCHAR(128) COMMENT '供应商名称',
  `currency_id` BIGINT UNSIGNED NOT NULL COMMENT '价格币种',
  `price_unit_id` BIGINT UNSIGNED NOT NULL COMMENT '价格对应单位',
  `unit_price` DECIMAL(20,8) NOT NULL COMMENT '单价',
  `effective_from` DATETIME COMMENT '生效开始',
  `effective_to` DATETIME COMMENT '生效结束',
  `source_name` VARCHAR(128) COMMENT '价格来源',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_material_price_material (material_id),
  KEY idx_material_price_region (region_id),
  KEY idx_material_price_currency (currency_id),
  KEY idx_material_price_unit (price_unit_id),
  CONSTRAINT `fk_material_price_material_id` FOREIGN KEY (`material_id`) REFERENCES `material` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_material_price_region_id` FOREIGN KEY (`region_id`) REFERENCES `region` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_material_price_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_material_price_price_unit_id` FOREIGN KEY (`price_unit_id`) REFERENCES `unit` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='材料价格主数据，为后续标准成本、采购价维护和按区域/时间取价预留扩展能力。';

CREATE TABLE `region_cost_profile` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `profile_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '配置编码',
  `profile_name` VARCHAR(128) NOT NULL COMMENT '配置名称',
  `region_id` BIGINT UNSIGNED NOT NULL COMMENT '所属区域',
  `supplier_name` VARCHAR(128) COMMENT '工厂/供应商名称',
  `supplier_code` VARCHAR(64) COMMENT '工厂/供应商编号',
  `currency_id` BIGINT UNSIGNED NOT NULL COMMENT '基础货币',
  `operating_worker_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '操作工费率',
  `skilled_worker_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '技术工费率',
  `transfer_technician_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '调机技术员费率',
  `production_leader_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '生产领班费率',
  `inspector_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '检验员费率',
  `engineer_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '工程师费率',
  `mold_fitter_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '模具钳工费率',
  `cost_interest_rate` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '财务成本利率',
  `benefits_one_shift` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '福利一班制',
  `benefits_two_shift` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '福利两班制',
  `benefits_three_shift` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '福利三班制',
  `factory_rent` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '厂房租金',
  `office_fee` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '办公费用',
  `electricity_fee` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '电费',
  `water_fee` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '水费',
  `gas_fee` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '煤气费',
  `effective_from` DATETIME COMMENT '生效开始',
  `effective_to` DATETIME COMMENT '生效结束',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_region_cost_profile_code (profile_code),
  KEY idx_region_cost_profile_region (region_id),
  KEY idx_region_cost_profile_currency (currency_id),
  CONSTRAINT `fk_region_cost_profile_region_id` FOREIGN KEY (`region_id`) REFERENCES `region` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_region_cost_profile_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='区域成本配置，对应低代码 regionCost。采用 profile 设计支持历史版本和不同工厂/供应商场景。';

CREATE TABLE `part` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `part_number` VARCHAR(64) UNIQUE NOT NULL COMMENT '零件编码',
  `part_name` VARCHAR(128) NOT NULL COMMENT '零件名称',
  `part_description` TEXT COMMENT '零件描述',
  `part_type` VARCHAR(64) COMMENT '零件类型',
  `part_version` VARCHAR(64) COMMENT '零件版本',
  `process_type` VARCHAR(64) COMMENT '工艺类型',
  `material_category_id` BIGINT UNSIGNED COMMENT '所属物料类型',
  `preferred_material_id` BIGINT UNSIGNED COMMENT '默认物料',
  `quantity_unit_id` BIGINT UNSIGNED COMMENT '数量单位',
  `surface_area` DECIMAL(20,8) COMMENT '表面积',
  `volume` DECIMAL(20,8) COMMENT '体积',
  `cad_file_url` VARCHAR(255) COMMENT 'CAD 文件地址',
  `target_url` VARCHAR(255) COMMENT '跳转地址',
  `legacy_result` TEXT COMMENT '旧系统 result 字段兼容',
  `legacy_msg` TEXT COMMENT '旧系统 msg 字段兼容',
  `lifecycle_status` VARCHAR(64) NOT NULL DEFAULT 'DRAFT' COMMENT '生命周期状态',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_part_number (part_number),
  KEY idx_part_material_category (material_category_id),
  KEY idx_part_material (preferred_material_id),
  KEY idx_part_quantity_unit (quantity_unit_id),
  CONSTRAINT `fk_part_material_category_id` FOREIGN KEY (`material_category_id`) REFERENCES `material_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_part_preferred_material_id` FOREIGN KEY (`preferred_material_id`) REFERENCES `material` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_part_quantity_unit_id` FOREIGN KEY (`quantity_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='零件主数据，对应低代码 Part，也是课设要求中的核心业务对象。';

CREATE TABLE `part_attachment` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `part_id` BIGINT UNSIGNED NOT NULL COMMENT '零件',
  `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
  `file_url` VARCHAR(255) NOT NULL COMMENT '文件地址',
  `file_type` VARCHAR(64) COMMENT '文件类型',
  `file_size` BIGINT COMMENT '文件大小',
  `source_type` VARCHAR(64) NOT NULL DEFAULT 'UPLOAD' COMMENT '来源类型',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY idx_part_attachment_part (part_id),
  CONSTRAINT `fk_part_attachment_part_id` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='零件附件表，用于扩展低代码中的 partCADFile，为未来图纸/工艺文件/说明书预留。';

CREATE TABLE `bom` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `part_id` BIGINT UNSIGNED NOT NULL COMMENT '父零件',
  `bom_code` VARCHAR(64) NOT NULL COMMENT 'BOM 编码',
  `bom_name` VARCHAR(128) COMMENT 'BOM 名称',
  `version_no` VARCHAR(64) NOT NULL DEFAULT 'V1' COMMENT '版本号',
  `status` VARCHAR(32) NOT NULL DEFAULT 'DRAFT' COMMENT '状态',
  `effective_from` DATETIME COMMENT '生效开始',
  `effective_to` DATETIME COMMENT '生效结束',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_bom_code (bom_code),
  UNIQUE KEY uk_bom_part_version (part_id, version_no),
  CONSTRAINT `fk_bom_part_id` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='BOM 头表。将低代码 Item 的层级关系升级为标准 BOM 结构，便于版本化与事务治理。';

CREATE TABLE `bom_item` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `bom_id` BIGINT UNSIGNED NOT NULL COMMENT '所属 BOM',
  `parent_item_id` BIGINT UNSIGNED COMMENT '父级 BOM 明细',
  `child_part_id` BIGINT UNSIGNED NOT NULL COMMENT '子零件',
  `item_name_snapshot` VARCHAR(128) COMMENT '子项名称快照',
  `item_number_snapshot` VARCHAR(64) COMMENT '子项编码快照',
  `item_version_snapshot` VARCHAR(64) COMMENT '子项版本快照',
  `quantity` DECIMAL(20,8) NOT NULL DEFAULT 1 COMMENT '用量',
  `quantity_unit_id` BIGINT UNSIGNED COMMENT '数量单位',
  `is_outsourced` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否外协',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT '排序号',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_bom_item_bom (bom_id),
  KEY idx_bom_item_parent (parent_item_id),
  KEY idx_bom_item_child_part (child_part_id),
  KEY idx_bom_item_quantity_unit (quantity_unit_id),
  CONSTRAINT `fk_bom_item_bom_id` FOREIGN KEY (`bom_id`) REFERENCES `bom` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bom_item_parent_item_id` FOREIGN KEY (`parent_item_id`) REFERENCES `bom_item` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_bom_item_child_part_id` FOREIGN KEY (`child_part_id`) REFERENCES `part` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_bom_item_quantity_unit_id` FOREIGN KEY (`quantity_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='BOM 明细表，支持多级 BOM、自关联、外协标识、快照字段。';

CREATE TABLE `equipment_category` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `category_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '分类编码',
  `category_name` VARCHAR(128) NOT NULL COMMENT '分类名称',
  `parent_id` BIGINT UNSIGNED COMMENT '父分类',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_equipment_category_code (category_code),
  KEY idx_equipment_category_parent (parent_id),
  CONSTRAINT `fk_equipment_category_parent_id` FOREIGN KEY (`parent_id`) REFERENCES `equipment_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备分类树，对应低代码 machineClassificaiton。';

CREATE TABLE `equipment` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `equipment_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '设备编码',
  `equipment_name` VARCHAR(128) NOT NULL COMMENT '设备名称',
  `category_id` BIGINT UNSIGNED COMMENT '设备分类',
  `equipment_type` VARCHAR(64) COMMENT '设备类型',
  `manufacturer` VARCHAR(128) COMMENT '制造商',
  `energy_type` VARCHAR(64) COMMENT '能源类型',
  `specification_text` VARCHAR(255) COMMENT '规格说明',
  `scale_desc` VARCHAR(128) COMMENT '规模/能力说明',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_equipment_code (equipment_code),
  KEY idx_equipment_category (category_id),
  CONSTRAINT `fk_equipment_category_id` FOREIGN KEY (`category_id`) REFERENCES `equipment_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备主数据，对应低代码 machine，但将旧模型中混杂的成本计算字段拆到费率/成本快照表。';

CREATE TABLE `equipment_specification` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `equipment_id` BIGINT UNSIGNED NOT NULL COMMENT '设备',
  `spec_key` VARCHAR(64) NOT NULL COMMENT '规格项',
  `spec_value` VARCHAR(255) NOT NULL COMMENT '规格值',
  `spec_unit_id` BIGINT UNSIGNED COMMENT '规格单位',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT '排序号',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_equipment_spec_equipment (equipment_id),
  KEY idx_equipment_spec_unit (spec_unit_id),
  CONSTRAINT `fk_equipment_specification_equipment_id` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_equipment_specification_spec_unit_id` FOREIGN KEY (`spec_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备规格扩展表，对应低代码 machineSpecification。采用 K-V 设计避免频繁改表。';

CREATE TABLE `equipment_rate` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `rate_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '费率编码',
  `equipment_id` BIGINT UNSIGNED COMMENT '适用设备',
  `equipment_category_id` BIGINT UNSIGNED COMMENT '适用设备分类',
  `description` VARCHAR(255) COMMENT '设备描述',
  `equipment_type` VARCHAR(64) COMMENT '设备类型',
  `manpower` INT NOT NULL DEFAULT 0 COMMENT '人力',
  `labor_group` VARCHAR(64) COMMENT '劳动力组',
  `direct_labor` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '直接人工',
  `direct_fringe` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '附加直接人工',
  `indirect_labor` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '间接人工',
  `indirect_fringe` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '附加间接人工',
  `total_labor` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '总人工',
  `depreciation` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '折旧',
  `insurance` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '保险',
  `floor_space` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '楼面面积',
  `mro_labor` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '维护人工',
  `utilities` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '水电煤',
  `indirect_materials` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '间接材料',
  `other_burden` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '其他费用',
  `total_burden` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '总负担',
  `total_minute_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '每分钟费用',
  `investment` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '投入',
  `currency_id` BIGINT UNSIGNED COMMENT '币种',
  `effective_from` DATETIME COMMENT '生效开始',
  `effective_to` DATETIME COMMENT '生效结束',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_equipment_rate_code (rate_code),
  KEY idx_equipment_rate_equipment (equipment_id),
  KEY idx_equipment_rate_category (equipment_category_id),
  KEY idx_equipment_rate_currency (currency_id),
  CONSTRAINT `fk_equipment_rate_equipment_id` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_equipment_rate_equipment_category_id` FOREIGN KEY (`equipment_category_id`) REFERENCES `equipment_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_equipment_rate_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备费率配置，对应低代码 machineRate，可作用于具体设备或设备分类，并支持历史生效区间。';

CREATE TABLE `equipment_cost_profile` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `equipment_id` BIGINT UNSIGNED NOT NULL COMMENT '设备',
  `profile_name` VARCHAR(128) NOT NULL COMMENT '成本配置名称',
  `equipment_number_snapshot` VARCHAR(64) COMMENT '设备编号快照',
  `manufacturer_snapshot` VARCHAR(128) COMMENT '制造商快照',
  `technical_reliability` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '技术可靠性',
  `currency_id` BIGINT UNSIGNED NOT NULL COMMENT '币种',
  `acquisition_value` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '购置价值',
  `number_of_equipment` DECIMAL(20,8) NOT NULL DEFAULT 1 COMMENT '设备数量',
  `annual_production_hours` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '年生产小时',
  `equipment_efficiency` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '设备效率',
  `installation_expenses` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '安装费用',
  `foundation_expenses` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '地基费用',
  `other_expenses` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '其他费用',
  `residual_value` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '残值',
  `equipment_lifespan_years` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '设备寿命(年)',
  `estimated_depreciation` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '折旧',
  `interest_rate` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '利率',
  `total_area_required` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '占地面积',
  `production_site_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '场地费用',
  `rated_power` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '额定功率',
  `electricity_usage_ratio` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '用电比例',
  `power_cost_electricity` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '电力成本',
  `maintenance_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '维护成本',
  `auxiliary_material_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '辅助材料成本',
  `total_fixed_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '固定成本合计',
  `total_variable_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '变动成本合计',
  `cost_per_unit_time` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '单位时间成本',
  `hourly_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '小时费率',
  `equipment_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '设备成本',
  `investment` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '投入',
  `asset_status` VARCHAR(32) COMMENT '新购/存量等状态',
  `effective_from` DATETIME COMMENT '生效开始',
  `effective_to` DATETIME COMMENT '生效结束',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_equipment_cost_profile_equipment (equipment_id),
  KEY idx_equipment_cost_profile_currency (currency_id),
  CONSTRAINT `fk_equipment_cost_profile_equipment_id` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_equipment_cost_profile_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备资本成本/小时成本配置，对应低代码 machineCost。作为工序成本计算的标准成本快照来源。';

CREATE TABLE `cost_calculation` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `calculation_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '计算单编码',
  `calculation_name` VARCHAR(128) NOT NULL COMMENT '计算名称',
  `part_id` BIGINT UNSIGNED NOT NULL COMMENT '关联零件',
  `manufacturing_region_id` BIGINT UNSIGNED COMMENT '制造区域',
  `region_cost_profile_id` BIGINT UNSIGNED COMMENT '区域成本配置',
  `currency_id` BIGINT UNSIGNED NOT NULL COMMENT '成本币种',
  `unit_id` BIGINT UNSIGNED COMMENT '数量单位',
  `material_category_id` BIGINT UNSIGNED COMMENT '默认材料类型',
  `material_id` BIGINT UNSIGNED COMMENT '默认材料',
  `procurement_type` VARCHAR(64) COMMENT '采购类型',
  `annual_effective_hours` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '年有效小时',
  `daily_production_shifts` INT NOT NULL DEFAULT 0 COMMENT '每日班次数',
  `production_hours_per_shift` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '每班小时数',
  `weekly_production_days` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '每周生产天数',
  `extra_shift_changes_per_week` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '每周额外换班次数',
  `annual_production_weeks` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '年生产周数',
  `annual_demand_qualified` INT NOT NULL DEFAULT 0 COMMENT '年合格品需求',
  `annual_other_demand` INT NOT NULL DEFAULT 0 COMMENT '年其他需求',
  `manufacturing_batch` INT NOT NULL DEFAULT 0 COMMENT '制造批次',
  `part_lifecycle_years` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '零件生命周期',
  `production_start_date` DATETIME COMMENT '投产日期',
  `net_selling_price` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '净售价',
  `part_dev_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '零件开发成本',
  `part_pro_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '零件生产准备成本',
  `pack_transport_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '包装运输成本',
  `sales_manage_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '销售管理成本',
  `dev_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '开发费用',
  `commercial_risk_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '商业风险成本',
  `inventory_interest_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '库存利息',
  `other_expenses` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '其他费用',
  `direct_management_fees` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '直接管理费',
  `profit_amount` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '利润',
  `account_period_discounts` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '账期折扣',
  `discounts` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '折扣',
  `transport_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '运输费',
  `tariff_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '关税',
  `indirect_costs` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '间接费用',
  `material_scrap_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '材料报废成本',
  `indirect_material_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '材料间接费用',
  `material_inventory_interest` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '材料库存利息',
  `overall_equipment_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '设备总成本',
  `total_changeover_expense` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '换模/调机总费用',
  `direct_labor_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '直接人工成本',
  `manufacturing_cost_1` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '制造成本1',
  `direct_labor_average_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '平均直接人工成本',
  `legacy_material_category_name` VARCHAR(128) COMMENT '兼容旧系统字段',
  `legacy_substance_name` VARCHAR(128) COMMENT '兼容旧系统字段',
  `snapshot_json` JSON COMMENT '扩展快照',
  `status` VARCHAR(32) NOT NULL DEFAULT 'DRAFT' COMMENT '状态',
  `version_no` INT NOT NULL DEFAULT 1 COMMENT '版本号',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `remark` VARCHAR(255) COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_cost_calculation_code (calculation_code),
  KEY idx_cost_calculation_part (part_id),
  KEY idx_cost_calculation_region (manufacturing_region_id),
  KEY idx_cost_calculation_region_cost_profile (region_cost_profile_id),
  KEY idx_cost_calculation_currency (currency_id),
  KEY idx_cost_calculation_unit (unit_id),
  KEY idx_cost_calculation_material_category (material_category_id),
  KEY idx_cost_calculation_material (material_id),
  CONSTRAINT `fk_cost_calculation_part_id` FOREIGN KEY (`part_id`) REFERENCES `part` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_calculation_manufacturing_region_id` FOREIGN KEY (`manufacturing_region_id`) REFERENCES `region` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_calculation_region_cost_profile_id` FOREIGN KEY (`region_cost_profile_id`) REFERENCES `region_cost_profile` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_calculation_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_calculation_unit_id` FOREIGN KEY (`unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_calculation_material_category_id` FOREIGN KEY (`material_category_id`) REFERENCES `material_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_calculation_material_id` FOREIGN KEY (`material_id`) REFERENCES `material` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成本计算头表/快照表，对应低代码 costCalculation，是整个成本场景的聚合根。';

CREATE TABLE `cost_material_item` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `cost_calculation_id` BIGINT UNSIGNED NOT NULL COMMENT '所属成本计算',
  `material_id` BIGINT UNSIGNED COMMENT '材料主数据',
  `material_category_id` BIGINT UNSIGNED COMMENT '材料分类',
  `material_name_snapshot` VARCHAR(128) COMMENT '材料名称快照',
  `material_code_snapshot` VARCHAR(64) COMMENT '材料编码快照',
  `quantity` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '数量',
  `quantity_unit_id` BIGINT UNSIGNED COMMENT '数量单位',
  `price` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '价格',
  `price_unit_currency_id` BIGINT UNSIGNED COMMENT '价格币种',
  `unit_price` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '单位价格',
  `density` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '密度',
  `density_unit_id` BIGINT UNSIGNED COMMENT '密度单位',
  `net_weight` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '净重',
  `feed_weight` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '理论投料重量',
  `feed_loss_rate` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '材料损失率',
  `effective_feed_weight` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '有效配重',
  `standard_material_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '标准材料成本',
  `waste_income` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '废料收益',
  `waste_expense` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '废料支出',
  `direct_material_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '直接材料成本',
  `scrap_material_name` VARCHAR(128) COMMENT '废料名称',
  `scrap_material_id` BIGINT UNSIGNED COMMENT '废料主数据',
  `scrap_weight` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '废料重量',
  `scrap_price` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '废料价格',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT '排序号',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_cost_material_item_calc (cost_calculation_id),
  KEY idx_cost_material_item_material (material_id),
  KEY idx_cost_material_item_category (material_category_id),
  KEY idx_cost_material_item_quantity_unit (quantity_unit_id),
  KEY idx_cost_material_item_currency (price_unit_currency_id),
  KEY idx_cost_material_item_density_unit (density_unit_id),
  KEY idx_cost_material_item_scrap_material (scrap_material_id),
  CONSTRAINT `fk_cost_material_item_cost_calculation_id` FOREIGN KEY (`cost_calculation_id`) REFERENCES `cost_calculation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_material_item_material_id` FOREIGN KEY (`material_id`) REFERENCES `material` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_material_item_material_category_id` FOREIGN KEY (`material_category_id`) REFERENCES `material_category` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_material_item_quantity_unit_id` FOREIGN KEY (`quantity_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_material_item_price_unit_currency_id` FOREIGN KEY (`price_unit_currency_id`) REFERENCES `currency` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_material_item_density_unit_id` FOREIGN KEY (`density_unit_id`) REFERENCES `unit` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_material_item_scrap_material_id` FOREIGN KEY (`scrap_material_id`) REFERENCES `material` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='材料成本明细，对应低代码 materialCost。保留有效配重、废料收益/支出、直接材料成本等逻辑字段。';

CREATE TABLE `process_operation` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `cost_calculation_id` BIGINT UNSIGNED NOT NULL COMMENT '所属成本计算',
  `process_no` INT NOT NULL DEFAULT 1 COMMENT '工序序号',
  `process_name` VARCHAR(128) NOT NULL COMMENT '工序名称',
  `process_type` VARCHAR(64) COMMENT '工序类型',
  `cycle_time` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '节拍时间',
  `parts_number` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '零件数量/穴数',
  `machine_efficiency` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '设备效率',
  `changeover_time` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '换模/调机时间',
  `scrap_rate` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '报废率',
  `product_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '生产率',
  `yearly_hours` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '年工时',
  `associated_equipment_id` BIGINT UNSIGNED COMMENT '关联设备',
  `associated_equipment_cost_profile_id` BIGINT UNSIGNED COMMENT '关联设备成本配置',
  `associated_equipment_rate_id` BIGINT UNSIGNED COMMENT '关联设备费率',
  `equipment_changeover_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '设备换模成本',
  `changeover_labor_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '换模人工成本',
  `total_changeover_expense` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '换模总费用',
  `direct_labor_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '直接人工成本',
  `start_date` DATETIME COMMENT '开始时间',
  `overall_equipment_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '设备总成本',
  `manufacturing_cost_1` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '制造成本1',
  `direct_labor_average_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '平均直接人工成本',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_process_operation_calc (cost_calculation_id),
  KEY idx_process_operation_equipment (associated_equipment_id),
  KEY idx_process_operation_equipment_profile (associated_equipment_cost_profile_id),
  KEY idx_process_operation_equipment_rate (associated_equipment_rate_id),
  CONSTRAINT `fk_process_operation_cost_calculation_id` FOREIGN KEY (`cost_calculation_id`) REFERENCES `cost_calculation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_process_operation_associated_equipment_id` FOREIGN KEY (`associated_equipment_id`) REFERENCES `equipment` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_process_operation_associated_equipment_cost_profile_id` FOREIGN KEY (`associated_equipment_cost_profile_id`) REFERENCES `equipment_cost_profile` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_process_operation_associated_equipment_rate_id` FOREIGN KEY (`associated_equipment_rate_id`) REFERENCES `equipment_rate` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='制造工序明细，对应低代码 Process。工序与成本计算是一对多关系。';

CREATE TABLE `process_equipment_usage` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `process_operation_id` BIGINT UNSIGNED NOT NULL COMMENT '所属工序',
  `equipment_id` BIGINT UNSIGNED COMMENT '设备',
  `equipment_cost_profile_id` BIGINT UNSIGNED COMMENT '设备成本配置',
  `equipment_rate_id` BIGINT UNSIGNED COMMENT '设备费率',
  `quantity` DECIMAL(20,8) NOT NULL DEFAULT 1 COMMENT '设备数量',
  `acquisition_value` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '购置值',
  `hourly_rate` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '小时费率',
  `equipment_cost_per_unit_time` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '单位时间设备成本',
  `runtime_minutes` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '运行分钟数',
  `setup_minutes` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '准备分钟数',
  `direct_machine_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '直接设备成本',
  `direct_labor_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '直接人工',
  `tooling_split_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '模具/工装分摊',
  `tooling_maintenance_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '模具/设备维护',
  `transfer_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '调机/转移成本',
  `manufacturing_cost_1` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '制造成本1',
  `other_manufacturing_overhead` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '其他制造间接费',
  `reject_ratio` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '报废比例',
  `manufacturing_cost_2` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '制造成本2',
  `total_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '总成本',
  `manufacturing_cost_3` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '制造成本3',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_process_equipment_usage_process (process_operation_id),
  KEY idx_process_equipment_usage_equipment (equipment_id),
  KEY idx_process_equipment_usage_profile (equipment_cost_profile_id),
  KEY idx_process_equipment_usage_rate (equipment_rate_id),
  CONSTRAINT `fk_process_equipment_usage_process_operation_id` FOREIGN KEY (`process_operation_id`) REFERENCES `process_operation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_process_equipment_usage_equipment_id` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_process_equipment_usage_equipment_cost_profile_id` FOREIGN KEY (`equipment_cost_profile_id`) REFERENCES `equipment_cost_profile` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_process_equipment_usage_equipment_rate_id` FOREIGN KEY (`equipment_rate_id`) REFERENCES `equipment_rate` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工序-设备用量/成本明细，用于承接旧模型 machine 中混合的工序设备成本结果。';

CREATE TABLE `formula_definition` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `formula_code` VARCHAR(64) UNIQUE NOT NULL COMMENT '公式编码',
  `formula_name` VARCHAR(128) NOT NULL COMMENT '公式名称',
  `formula_category` VARCHAR(64) NOT NULL COMMENT '公式类别',
  `expression_text` TEXT NOT NULL COMMENT '公式表达式',
  `description` TEXT COMMENT '公式说明',
  `input_schema_json` JSON COMMENT '输入结构',
  `output_schema_json` JSON COMMENT '输出结构',
  `version_no` INT NOT NULL DEFAULT 1 COMMENT '版本号',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_formula_code (formula_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公式定义表，用于保存可解释的成本计算公式，为后续公式版本化和 LLM 解释提供底座。';

CREATE TABLE `cost_component` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `cost_calculation_id` BIGINT UNSIGNED NOT NULL COMMENT '所属成本计算',
  `component_group` VARCHAR(64) NOT NULL COMMENT '成本大类',
  `component_code` VARCHAR(64) NOT NULL COMMENT '成本项编码',
  `component_name` VARCHAR(128) NOT NULL COMMENT '成本项名称',
  `amount` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '金额',
  `currency_id` BIGINT UNSIGNED COMMENT '币种',
  `source_table` VARCHAR(64) COMMENT '来源表',
  `source_record_id` BIGINT UNSIGNED COMMENT '来源记录',
  `material_item_id` BIGINT UNSIGNED COMMENT '来源材料明细',
  `process_operation_id` BIGINT UNSIGNED COMMENT '来源工序',
  `equipment_usage_id` BIGINT UNSIGNED COMMENT '来源工序设备',
  `formula_id` BIGINT UNSIGNED COMMENT '来源公式',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT '排序号',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_cost_component_calc (cost_calculation_id),
  KEY idx_cost_component_currency (currency_id),
  KEY idx_cost_component_material (material_item_id),
  KEY idx_cost_component_process (process_operation_id),
  KEY idx_cost_component_equipment_usage (equipment_usage_id),
  KEY idx_cost_component_formula (formula_id),
  CONSTRAINT `fk_cost_component_cost_calculation_id` FOREIGN KEY (`cost_calculation_id`) REFERENCES `cost_calculation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_component_currency_id` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_component_material_item_id` FOREIGN KEY (`material_item_id`) REFERENCES `cost_material_item` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_component_process_operation_id` FOREIGN KEY (`process_operation_id`) REFERENCES `process_operation` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_component_equipment_usage_id` FOREIGN KEY (`equipment_usage_id`) REFERENCES `process_equipment_usage` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_component_formula_id` FOREIGN KEY (`formula_id`) REFERENCES `formula_definition` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通用成本构成明细表。既覆盖课设 CostItem 需求，又避免未来新增成本类别时频繁改表。';

CREATE TABLE `cost_summary` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `cost_calculation_id` BIGINT UNSIGNED UNIQUE NOT NULL COMMENT '所属成本计算',
  `material_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '材料成本合计',
  `manufacture_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '制造成本合计',
  `special_direct_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '特殊直接成本合计',
  `period_expenses_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '期间费用合计',
  `account_period_discounts_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '账期折扣合计',
  `transport_tariff_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '运输关税合计',
  `indirect_costs_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '间接成本合计',
  `profit_total` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '利润',
  `total_cost` DECIMAL(20,8) NOT NULL DEFAULT 0 COMMENT '总成本',
  `result_currency_id` BIGINT UNSIGNED COMMENT '结果币种',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_cost_summary_calc (cost_calculation_id),
  KEY idx_cost_summary_currency (result_currency_id),
  CONSTRAINT `fk_cost_summary_cost_calculation_id` FOREIGN KEY (`cost_calculation_id`) REFERENCES `cost_calculation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_summary_result_currency_id` FOREIGN KEY (`result_currency_id`) REFERENCES `currency` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成本汇总表，对应旧模型中的总计字段与 ManufacturingCost1 汇总口径，供报表与图表快速读取。';

CREATE TABLE `cost_trace` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `cost_calculation_id` BIGINT UNSIGNED NOT NULL COMMENT '所属成本计算',
  `source_table` VARCHAR(64) NOT NULL COMMENT '来源表',
  `source_record_id` BIGINT UNSIGNED COMMENT '来源记录',
  `trace_step` VARCHAR(128) NOT NULL COMMENT '追溯步骤',
  `input_payload_json` JSON COMMENT '输入快照',
  `formula_id` BIGINT UNSIGNED COMMENT '使用公式',
  `output_payload_json` JSON COMMENT '输出快照',
  `remark` VARCHAR(255) COMMENT '备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY idx_cost_trace_calc (cost_calculation_id),
  KEY idx_cost_trace_formula (formula_id),
  CONSTRAINT `fk_cost_trace_cost_calculation_id` FOREIGN KEY (`cost_calculation_id`) REFERENCES `cost_calculation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cost_trace_formula_id` FOREIGN KEY (`formula_id`) REFERENCES `formula_definition` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成本追溯表，用于记录关键计算步骤的输入、公式、输出，满足课设中“结果可追溯”的高分要求。';

CREATE TABLE `meta_table_definition` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `table_name` VARCHAR(64) UNIQUE NOT NULL COMMENT '表名',
  `display_name` VARCHAR(128) NOT NULL COMMENT '显示名',
  `domain_name` VARCHAR(64) NOT NULL COMMENT '所属域',
  `description` TEXT COMMENT '表描述',
  `is_core` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否核心表',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY uk_meta_table_name (table_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表级元数据字典，支撑课设要求中的数据地图和元数据页面。';

CREATE TABLE `meta_column_definition` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `table_def_id` BIGINT UNSIGNED NOT NULL COMMENT '所属表元数据',
  `column_name` VARCHAR(64) NOT NULL COMMENT '字段名',
  `display_name` VARCHAR(128) NOT NULL COMMENT '显示名',
  `description` TEXT COMMENT '字段描述',
  `data_type` VARCHAR(64) NOT NULL COMMENT '数据类型',
  `is_primary_key` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否主键',
  `is_foreign_key` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否外键',
  `ref_table_name` VARCHAR(64) COMMENT '引用表',
  `ref_column_name` VARCHAR(64) COMMENT '引用字段',
  `is_nullable` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否可空',
  `sort_no` INT NOT NULL DEFAULT 1 COMMENT '排序号',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY idx_meta_column_table (table_def_id),
  CONSTRAINT `fk_meta_column_definition_table_def_id` FOREIGN KEY (`table_def_id`) REFERENCES `meta_table_definition` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='字段级元数据字典，记录字段名称、含义、是否主外键、引用关系等。';