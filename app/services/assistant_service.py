import json
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import requests
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.bom import Bom
from app.models.bom_item import BomItem
from app.models.cost_item import CostItem
from app.models.currency import Currency
from app.models.material import Material
from app.models.material_category import MaterialCategory
from app.models.material_type import MaterialType
from app.models.part import Part
from app.models.unit import Unit


class AssistantService:
    def __init__(self, db: Session):
        self.db = db

    def capabilities(self) -> dict[str, Any]:
        api_key = self._effective_api_key()
        return {
            "llm_enabled": bool(settings.llm_enabled),
            "llm_configured": bool(api_key),
            "provider_style": settings.llm_api_style,
            "model": settings.llm_model,
            "features": [
                "系统操作指南问答",
                "元数据与数据地图检索解释",
                "通过聊天框导入结构化工作流数据",
                "零件/BOM/成本计算结果分析建议",
                "按当前页面上下文回答",
            ],
        }

    def chat(
        self,
        message: str,
        history: list[dict[str, str]],
        context: dict[str, Any] | None,
        use_runtime_snapshot: bool = True,
        runtime_api_key: str | None = None,
    ) -> dict[str, Any]:
        clean_message = message.strip()
        if not clean_message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="消息不能为空")

        context_data = dict(context or {})
        metadata_context = self._metadata_context(clean_message)
        workflow_import = self._workflow_import_by_message(clean_message)
        runtime_context = self._runtime_snapshot() if use_runtime_snapshot else {}
        part_context = self._part_context(context_data)
        explicit_lookup = self._lookup_cost_by_message(clean_message)
        entity_hits = self._entity_lookup_by_message(clean_message)

        context_used = {
            "ui_context": context_data,
            "runtime_snapshot": runtime_context,
            "part_context": part_context,
            "explicit_part_cost_lookup": explicit_lookup,
            "entity_hits": entity_hits,
            "metadata_tables": metadata_context.get("table_names", []),
            "workflow_import": workflow_import,
        }

        direct_answer = self._direct_answer_by_message(clean_message, context_used)
        if direct_answer:
            return {
                "answer": direct_answer,
                "suggestions": self._suggestions_by_question(clean_message),
                "model": settings.llm_model,
                "provider_style": settings.llm_api_style,
                "context_used": context_used,
            }

        if not settings.llm_enabled:
            return self._fallback_answer(clean_message, context_used)

        if not self._effective_api_key(runtime_api_key):
            return self._fallback_answer(clean_message, context_used, no_key=True)

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            clean_message=clean_message,
            context_used=context_used,
            metadata_context=metadata_context,
        )

        answer = self._invoke_llm(
            system_prompt=system_prompt,
            history=history,
            user_prompt=user_prompt,
            runtime_api_key=runtime_api_key,
        )
        return {
            "answer": answer,
            "suggestions": self._suggestions_by_question(clean_message),
            "model": settings.llm_model,
            "provider_style": settings.llm_api_style,
            "context_used": context_used,
        }

    def _invoke_llm(
        self,
        system_prompt: str,
        history: list[dict[str, str]],
        user_prompt: str,
        runtime_api_key: str | None = None,
    ) -> str:
        style = (settings.llm_api_style or "openai").lower()
        base_url = settings.llm_base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {self._effective_api_key(runtime_api_key)}",
            "Content-Type": "application/json",
        }

        safe_history: list[dict[str, str]] = []
        for msg in history[-12:]:
            role = msg.get("role", "user")
            content = (msg.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                safe_history.append({"role": role, "content": content})

        if style in {"openai", "chat", "chat_completions"}:
            url = f"{base_url}/v1/chat/completions"
            messages = [{"role": "system", "content": system_prompt}] + safe_history + [
                {"role": "user", "content": user_prompt}
            ]
            payload = {
                "model": settings.llm_model,
                "messages": messages,
                "temperature": settings.llm_temperature,
            }
            answer = self._post_llm(url=url, headers=headers, payload=payload, style=style)
            if answer:
                return answer
        elif style in {"openai-response", "responses"}:
            url = f"{base_url}/v1/responses"
            inputs = [{"role": "system", "content": system_prompt}] + safe_history + [
                {"role": "user", "content": user_prompt}
            ]
            payload = {
                "model": settings.llm_model,
                "input": inputs,
                "temperature": settings.llm_temperature,
            }
            answer = self._post_llm(url=url, headers=headers, payload=payload, style=style)
            if answer:
                return answer
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"不支持的 LLM API 风格: {settings.llm_api_style}",
            )

        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM 未返回有效内容")

    def _post_llm(self, url: str, headers: dict[str, str], payload: dict[str, Any], style: str) -> str | None:
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=settings.llm_timeout_seconds)
        except requests.RequestException as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"LLM 调用失败: {exc}") from exc

        if resp.status_code >= 400:
            detail = ""
            try:
                detail = json.dumps(resp.json(), ensure_ascii=False)
            except Exception:
                detail = resp.text
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM 返回错误({resp.status_code}): {detail}",
            )

        data = resp.json()
        if style in {"openai", "chat", "chat_completions"}:
            try:
                return data["choices"][0]["message"]["content"].strip()
            except Exception:
                return None
        if style in {"openai-response", "responses"}:
            text_out = data.get("output_text")
            if isinstance(text_out, str) and text_out.strip():
                return text_out.strip()
            output = data.get("output") or []
            for item in output:
                for c in item.get("content", []):
                    if c.get("type") in {"output_text", "text"} and c.get("text"):
                        return str(c["text"]).strip()
        return None

    def _build_system_prompt(self) -> str:
        return (
            "你是零件成本管理系统内嵌AI助手。"
            "你的职责是帮助用户理解系统功能、数据含义、操作路径，并解释成本结果。"
            "必须基于给定上下文回答，不得编造不存在的表、字段或业务流程。"
            "当用户粘贴结构化JSON工作流数据时，系统会先尝试写入主数据、零件、BOM和成本记录，你需要解释导入结果。"
            "如果上下文不足，请明确指出并给出下一步建议。"
            "回答尽量结构化、简洁、可执行，默认使用中文。"
            "涉及成本建议时，优先给出可落地动作，例如“优先优化材料损耗率”并说明依据。"
        )

    def _build_user_prompt(
        self,
        clean_message: str,
        context_used: dict[str, Any],
        metadata_context: dict[str, Any],
    ) -> str:
        ops_guide = {
            "基础问答": [
                "数据配置用于维护单位、币种、区域、设备、物料等主数据。",
                "零件管理用于维护零件、BOM、附件及成本计算。",
                "元数据与数据地图用于查看表字段、主外键和表说明。",
            ],
            "成本分析入口": [
                "零件管理 -> 成本计算列表 -> 详情。",
                "详情页包含基础数据、材料成本、制造成本、间接费用、成本明细、结果分析。",
            ],
        }
        return (
            f"用户问题:\n{clean_message}\n\n"
            f"当前上下文(JSON):\n{json.dumps(context_used, ensure_ascii=False, default=str)}\n\n"
            f"系统操作指南(JSON):\n{json.dumps(ops_guide, ensure_ascii=False, default=str)}\n\n"
            f"元数据摘录(JSON):\n{json.dumps(metadata_context, ensure_ascii=False, default=str)}\n\n"
            "请基于以上内容回答。若涉及步骤，请给编号步骤。若涉及数据分析，请指出关键指标和建议。"
        )

    def _metadata_context(self, query: str) -> dict[str, Any]:
        metadata_path = Path(__file__).resolve().parents[2] / "frontend" / "metadata_dictionary.json"
        if not metadata_path.exists():
            return {"tables": [], "table_names": []}

        try:
            raw = metadata_path.read_text(encoding="utf-8")
            md = json.loads(raw)
        except Exception:
            return {"tables": [], "table_names": []}

        all_tables = md.get("tables") or []
        if not all_tables:
            return {"tables": [], "table_names": []}

        q = query.lower()
        matched = []
        for t in all_tables:
            t_name = str(t.get("table_name", ""))
            t_desc = str(t.get("table_description", ""))
            t_show = str(t.get("table_display_name", ""))
            hay = f"{t_name} {t_desc} {t_show}".lower()
            if not q or any(token in hay for token in q.split()):
                matched.append(t)
            if len(matched) >= 8:
                break
        if not matched:
            matched = all_tables[:6]

        slim_tables = []
        for t in matched:
            slim_fields = []
            for f in (t.get("fields") or [])[:10]:
                slim_fields.append(
                    {
                        "name": f.get("name"),
                        "type": f.get("data_type"),
                        "pk": bool(f.get("is_primary_key")),
                        "fk": bool(f.get("is_foreign_key")),
                        "references": f.get("references"),
                        "description": f.get("description"),
                        "module": f.get("module") or t.get("module"),
                    }
                )
            slim_tables.append(
                {
                    "table_name": t.get("table_name"),
                    "table_display_name": t.get("table_display_name"),
                    "table_description": t.get("table_description"),
                    "module": t.get("module"),
                    "fields": slim_fields,
                }
            )
        return {"tables": slim_tables, "table_names": [t.get("table_name") for t in slim_tables]}

    def _workflow_import_by_message(self, message: str) -> dict[str, Any] | None:
        data = self._extract_workflow_payload(message)
        if not data:
            return None

        if "workflow_data" in data and isinstance(data["workflow_data"], dict):
            data = data["workflow_data"]
        if "data" in data and isinstance(data["data"], dict):
            data = data["data"]

        accepted_keys = {
            "units",
            "currencies",
            "material_types",
            "material_categories",
            "materials",
            "parts",
            "boms",
            "bom_items",
            "cost_items",
        }
        if not any(k in data for k in accepted_keys):
            return None

        result: dict[str, Any] = {"created": {}, "skipped": {}, "errors": []}

        def _bump(bucket: str, name: str) -> None:
            result[bucket][name] = int(result[bucket].get(name, 0)) + 1

        try:
            for row in self._as_list(data.get("units")):
                code = self._clean_str(row.get("unit_code") or row.get("code"))
                if not code:
                    result["errors"].append("单位缺少 unit_code")
                    continue
                obj = self.db.scalars(select(Unit).where(Unit.unit_code == code)).first()
                if obj:
                    _bump("skipped", "units")
                    continue
                self.db.add(
                    Unit(
                        unit_code=code,
                        unit_name=self._clean_str(row.get("unit_name") or row.get("name") or code),
                        unit_display_name=self._clean_str(row.get("unit_display_name") or row.get("display_name")),
                        unit_category=self._clean_str(row.get("unit_category") or row.get("category") or "数量"),
                        measurement_system=self._clean_str(row.get("measurement_system")),
                        unit_factor=self._decimal(row.get("unit_factor"), Decimal("1")),
                        is_active=1 if row.get("is_active", True) else 0,
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "units")

            for row in self._as_list(data.get("currencies")):
                code = self._clean_str(row.get("currency_code") or row.get("code"))
                if not code:
                    result["errors"].append("币种缺少 currency_code")
                    continue
                obj = self.db.scalars(select(Currency).where(Currency.currency_code == code)).first()
                if obj:
                    _bump("skipped", "currencies")
                    continue
                self.db.add(
                    Currency(
                        currency_code=code,
                        currency_name=self._clean_str(row.get("currency_name") or row.get("name") or code),
                        currency_symbol=self._clean_str(row.get("currency_symbol") or row.get("symbol")),
                        precision_scale=int(row.get("precision_scale") or 2),
                        is_base_currency=1 if row.get("is_base_currency", False) else 0,
                        is_active=1 if row.get("is_active", True) else 0,
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "currencies")

            self.db.flush()

            for row in self._as_list(data.get("material_types")):
                code = self._clean_str(row.get("material_type_code") or row.get("code"))
                if not code:
                    result["errors"].append("物料类型缺少 material_type_code")
                    continue
                obj = self.db.scalars(select(MaterialType).where(MaterialType.material_type_code == code)).first()
                if obj:
                    _bump("skipped", "material_types")
                    continue
                self.db.add(
                    MaterialType(
                        material_type_code=code,
                        material_type_name=self._clean_str(row.get("material_type_name") or row.get("name") or code),
                        description=self._clean_str(row.get("description")),
                        is_active=1 if row.get("is_active", True) else 0,
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "material_types")

            for row in self._as_list(data.get("material_categories")):
                code = self._clean_str(row.get("category_code") or row.get("code"))
                if not code:
                    result["errors"].append("物质分类缺少 category_code")
                    continue
                obj = self.db.scalars(select(MaterialCategory).where(MaterialCategory.category_code == code)).first()
                if obj:
                    _bump("skipped", "material_categories")
                    continue
                self.db.add(
                    MaterialCategory(
                        category_code=code,
                        category_name=self._clean_str(row.get("category_name") or row.get("name") or code),
                        category_type=self._clean_str(row.get("category_type") or "SUBSTANCE"),
                        is_active=1 if row.get("is_active", True) else 0,
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "material_categories")

            self.db.flush()

            for row in self._as_list(data.get("materials")):
                code = self._clean_str(row.get("material_code") or row.get("code"))
                if not code:
                    result["errors"].append("物质缺少 material_code")
                    continue
                obj = self.db.scalars(select(Material).where(Material.material_code == code)).first()
                if obj:
                    _bump("skipped", "materials")
                    continue
                category_id = self._id_by_code(MaterialCategory, MaterialCategory.category_code, row.get("category_code")) or row.get("category_id")
                self.db.add(
                    Material(
                        material_code=code,
                        material_name=self._clean_str(row.get("material_name") or row.get("name") or code),
                        category_id=category_id,
                        density=self._decimal(row.get("density")),
                        density_unit_id=self._id_by_code(Unit, Unit.unit_code, row.get("density_unit_code")) or row.get("density_unit_id"),
                        default_quantity_unit_id=self._id_by_code(Unit, Unit.unit_code, row.get("default_quantity_unit_code")) or row.get("default_quantity_unit_id"),
                        specification=self._clean_str(row.get("specification")),
                        is_active=1 if row.get("is_active", True) else 0,
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "materials")

            self.db.flush()

            part_rows = self._as_list(data.get("parts"))
            for row in part_rows:
                code = self._clean_str(row.get("part_code") or row.get("part_number") or row.get("code"))
                if not code:
                    result["errors"].append("零件缺少 part_code")
                    continue
                obj = self.db.scalars(select(Part).where(Part.part_code == code)).first()
                if obj:
                    _bump("skipped", "parts")
                    continue
                self.db.add(
                    Part(
                        part_code=code,
                        part_name=self._clean_str(row.get("part_name") or row.get("name") or code),
                        part_description=self._clean_str(row.get("part_description") or row.get("description")),
                        part_type=self._clean_str(row.get("part_type") or row.get("type")),
                        material_category_id=self._id_by_code(MaterialCategory, MaterialCategory.category_code, row.get("material_category_code")) or row.get("material_category_id"),
                        material_type_id=self._id_by_code(MaterialType, MaterialType.material_type_code, row.get("material_type_code")) or row.get("material_type_id"),
                        preferred_material_id=self._id_by_code(Material, Material.material_code, row.get("preferred_material_code") or row.get("material_code")) or row.get("preferred_material_id"),
                        quantity_unit_id=self._id_by_code(Unit, Unit.unit_code, row.get("quantity_unit_code") or row.get("unit_code")) or row.get("quantity_unit_id"),
                        surface_area=self._decimal(row.get("surface_area")),
                        volume=self._decimal(row.get("volume")),
                        cad_file_url=self._clean_str(row.get("cad_file_url")),
                        target_url=self._clean_str(row.get("target_url")),
                        part_status=self._clean_str(row.get("part_status") or "DRAFT"),
                        lifecycle_stage=self._clean_str(row.get("lifecycle_stage") or "DESIGN"),
                        revision_no=self._clean_str(row.get("revision_no") or "A"),
                        version_no=int(row.get("version_no") or 1),
                        is_active=1 if row.get("is_active", True) else 0,
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "parts")

            self.db.flush()

            for row in self._as_list(data.get("boms")):
                code = self._clean_str(row.get("bom_code") or row.get("code"))
                part_id = self._id_by_code(Part, Part.part_code, row.get("part_code") or row.get("parent_part_code")) or row.get("part_id")
                if not code or not part_id:
                    result["errors"].append(f"BOM缺少 bom_code 或父零件: {code or '-'}")
                    continue
                obj = self.db.scalars(select(Bom).where(Bom.bom_code == code)).first()
                if obj:
                    _bump("skipped", "boms")
                    continue
                self.db.add(
                    Bom(
                        part_id=part_id,
                        bom_code=code,
                        bom_name=self._clean_str(row.get("bom_name") or row.get("name") or code),
                        version_no=self._clean_str(row.get("version_no") or "V1"),
                        status=self._clean_str(row.get("status") or "DRAFT"),
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "boms")

            self.db.flush()

            for row in self._as_list(data.get("bom_items")):
                bom_id = self._id_by_code(Bom, Bom.bom_code, row.get("bom_code")) or row.get("bom_id")
                child_part_id = self._id_by_code(Part, Part.part_code, row.get("child_part_code") or row.get("part_code")) or row.get("child_part_id")
                if not bom_id or not child_part_id:
                    result["errors"].append("BOM明细缺少 bom_code/bom_id 或 child_part_code")
                    continue
                child = self.db.get(Part, int(child_part_id))
                self.db.add(
                    BomItem(
                        bom_id=bom_id,
                        child_part_id=child_part_id,
                        item_name_snapshot=self._clean_str(row.get("item_name_snapshot")) or (child.part_name if child else None),
                        item_number_snapshot=self._clean_str(row.get("item_number_snapshot")) or (child.part_code if child else None),
                        item_version_snapshot=self._clean_str(row.get("item_version_snapshot")) or (child.revision_no if child else None),
                        quantity=self._decimal(row.get("quantity"), Decimal("1")),
                        quantity_unit_id=self._id_by_code(Unit, Unit.unit_code, row.get("quantity_unit_code") or row.get("unit_code")) or row.get("quantity_unit_id"),
                        is_outsourced=1 if row.get("is_outsourced", False) else 0,
                        sort_no=int(row.get("sort_no") or 1),
                        remark=self._clean_str(row.get("remark")),
                    )
                )
                _bump("created", "bom_items")

            for part_row in part_rows:
                cost = part_row.get("cost")
                if isinstance(cost, dict):
                    cost.setdefault("part_code", part_row.get("part_code") or part_row.get("part_number") or part_row.get("code"))
                    if not isinstance(data.get("cost_items"), list):
                        data["cost_items"] = []
                    data["cost_items"].append(cost)

            self.db.flush()

            for row in self._as_list(data.get("cost_items")):
                part_id = self._id_by_code(Part, Part.part_code, row.get("part_code") or row.get("part_number")) or row.get("part_id")
                currency_id = self._id_by_code(Currency, Currency.currency_code, row.get("currency_code")) or row.get("currency_id")
                if not part_id or not currency_id:
                    result["errors"].append("成本记录缺少 part_code/part_id 或 currency_code/currency_id")
                    continue
                material_cost = self._decimal(row.get("material_cost"), Decimal("0"))
                manufacturing_cost = self._decimal(row.get("manufacturing_cost"), Decimal("0"))
                overhead_cost = self._decimal(row.get("overhead_cost"), Decimal("0"))
                total_cost = self._decimal(row.get("total_cost"), material_cost + manufacturing_cost + overhead_cost)
                self.db.add(
                    CostItem(
                        id=self._next_bigint_id_for_sqlite(CostItem),
                        calculation_name=self._clean_str(row.get("calculation_name") or row.get("name") or "AI导入成本计算"),
                        part_id=part_id,
                        currency_id=currency_id,
                        unit_id=self._id_by_code(Unit, Unit.unit_code, row.get("unit_code")) or row.get("unit_id"),
                        material_cost=material_cost,
                        manufacturing_cost=manufacturing_cost,
                        overhead_cost=overhead_cost,
                        total_cost=total_cost,
                        rule_version=self._clean_str(row.get("rule_version") or "ai_import_v1"),
                        trace_detail=json.dumps(row.get("trace_detail") or row, ensure_ascii=False, default=str),
                        remark=self._clean_str(row.get("remark") or "AI助手结构化导入"),
                    )
                )
                _bump("created", "cost_items")

            if result["created"] or result["skipped"]:
                self.db.commit()
                return result
            self.db.rollback()
            return None
        except IntegrityError as exc:
            self.db.rollback()
            return {"created": result["created"], "skipped": result["skipped"], "errors": [f"数据库约束冲突: {exc.orig}"]}
        except Exception as exc:
            self.db.rollback()
            return {"created": result["created"], "skipped": result["skipped"], "errors": [f"导入失败: {exc}"]}

    def _extract_workflow_payload(self, message: str) -> dict[str, Any] | None:
        msg = message.strip()
        if not any(x in msg for x in ["导入", "录入", "创建", "写入", "workflow_data", "parts", "boms", "cost_items"]):
            return None
        candidates = re.findall(r"```(?:json)?\s*([\s\S]*?)```", msg, flags=re.IGNORECASE)
        candidates.append(msg)
        for candidate in candidates:
            text_body = candidate.strip()
            start = text_body.find("{")
            end = text_body.rfind("}")
            if start < 0 or end <= start:
                continue
            try:
                parsed = json.loads(text_body[start : end + 1])
            except Exception:
                continue
            if isinstance(parsed, dict):
                return parsed
        return None

    def _as_list(self, value: Any) -> list[dict[str, Any]]:
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
        if isinstance(value, dict):
            return [value]
        return []

    def _clean_str(self, value: Any) -> str | None:
        if value is None:
            return None
        text_value = str(value).strip()
        return text_value or None

    def _decimal(self, value: Any, default: Decimal | None = None) -> Decimal | None:
        if value is None or value == "":
            return default
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return default

    def _id_by_code(self, model: Any, column: Any, code: Any) -> int | None:
        code_text = self._clean_str(code)
        if not code_text:
            return None
        row = self.db.scalars(select(model).where(column == code_text)).first()
        return int(row.id) if row is not None else None

    def _next_bigint_id_for_sqlite(self, model: Any) -> int | None:
        if self.db.get_bind().dialect.name != "sqlite":
            return None
        current_max = self.db.execute(select(func.max(model.id))).scalar()
        return int(current_max or 0) + 1

    def _runtime_snapshot(self) -> dict[str, Any]:
        table_names = [
            "part",
            "bom",
            "bom_item",
            "cost_item",
            "material",
            "material_price",
            "equipment",
            "unit",
            "currency",
        ]
        table_counts: dict[str, int] = {}
        for t in table_names:
            try:
                count = self.db.execute(text(f"SELECT COUNT(1) FROM `{t}`")).scalar() or 0
            except Exception:
                count = 0
            table_counts[t] = int(count)

        latest_costs = self.db.execute(
            text(
                """
                SELECT ci.id, ci.calculation_name, ci.total_cost, c.currency_code, p.part_number AS part_code, p.part_name, ci.updated_at
                FROM cost_item ci
                LEFT JOIN currency c ON c.id = ci.currency_id
                LEFT JOIN part p ON p.id = ci.part_id
                ORDER BY ci.updated_at DESC, ci.id DESC
                LIMIT 5
                """
            )
        ).mappings().all()

        return {
            "table_counts": table_counts,
            "latest_cost_items": [dict(r) for r in latest_costs],
            "timestamp": datetime_now_text(),
        }

    def _part_context(self, context_data: dict[str, Any]) -> dict[str, Any]:
        part_id = context_data.get("selected_part_id")
        cost_item_id = context_data.get("selected_cost_item_id")
        out: dict[str, Any] = {}

        if part_id:
            part_row = self.db.execute(
                text(
                    """
                    SELECT p.id,
                           p.part_number AS part_code,
                           p.part_name,
                           p.process_type AS lifecycle_stage,
                           p.lifecycle_status AS part_status,
                           mt.material_type_name, u.unit_code
                    FROM part p
                    LEFT JOIN material_type mt ON mt.id = p.material_type_id
                    LEFT JOIN unit u ON u.id = p.quantity_unit_id
                    WHERE p.id = :part_id
                    """
                ),
                {"part_id": part_id},
            ).mappings().first()
            if part_row:
                out["selected_part"] = dict(part_row)

        if cost_item_id:
            ci_row = self.db.execute(
                text(
                    """
                    SELECT ci.id, ci.calculation_name, ci.material_cost, ci.manufacturing_cost,
                           ci.overhead_cost, ci.total_cost, c.currency_code, u.unit_code, ci.updated_at
                    FROM cost_item ci
                    LEFT JOIN currency c ON c.id = ci.currency_id
                    LEFT JOIN unit u ON u.id = ci.unit_id
                    WHERE ci.id = :cost_item_id
                    """
                ),
                {"cost_item_id": cost_item_id},
            ).mappings().first()
            if ci_row:
                out["selected_cost_item"] = dict(ci_row)
        elif part_id:
            latest_for_part = self._latest_cost_item_for_part(int(part_id))
            if latest_for_part:
                out["selected_cost_item"] = latest_for_part

        return out

    def _latest_cost_item_for_part(self, part_id: int) -> dict[str, Any] | None:
        ci_row = self.db.execute(
            text(
                """
                SELECT ci.id, ci.calculation_name, ci.material_cost, ci.manufacturing_cost,
                       ci.overhead_cost, ci.total_cost, c.currency_code, u.unit_code, ci.updated_at
                FROM cost_item ci
                LEFT JOIN currency c ON c.id = ci.currency_id
                LEFT JOIN unit u ON u.id = ci.unit_id
                WHERE ci.part_id = :part_id
                ORDER BY ci.updated_at DESC, ci.id DESC
                LIMIT 1
                """
            ),
            {"part_id": part_id},
        ).mappings().first()
        return dict(ci_row) if ci_row else None

    def _lookup_cost_by_message(self, message: str) -> dict[str, Any] | None:
        msg = (message or "").strip()
        if not msg:
            return None
        if not any(x in msg.lower() for x in ["成本", "占比", "cost", "ratio", "比例"]):
            return None

        candidates = set(re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", msg))
        candidates = {x for x in candidates if len(x) >= 4}

        # 1) 优先用疑似零件编号匹配
        for token in candidates:
            row = self.db.execute(
                text(
                    """
                    SELECT p.id, p.part_number AS part_code, p.part_name
                    FROM part p
                    WHERE UPPER(p.part_number) = UPPER(:token)
                    LIMIT 1
                    """
                ),
                {"token": token},
            ).mappings().first()
            if row:
                result = self._build_cost_ratio_payload(int(row["id"]))
                if result:
                    return result

        # 2) 再按“问题文本包含零件编码/名称”匹配
        try:
            row = self.db.execute(
                text(
                    """
                    SELECT p.id, p.part_number AS part_code, p.part_name
                    FROM part p
                    WHERE LOWER(:msg) LIKE CONCAT('%', LOWER(p.part_number), '%')
                       OR LOWER(:msg) LIKE CONCAT('%', LOWER(p.part_name), '%')
                    ORDER BY CHAR_LENGTH(p.part_number) DESC, p.id DESC
                    LIMIT 1
                    """
                ),
                {"msg": msg.lower()},
            ).mappings().first()
        except Exception:
            row = None
        if not row:
            return None
        return self._build_cost_ratio_payload(int(row["id"]))

    def _build_cost_ratio_payload(self, part_id: int) -> dict[str, Any] | None:
        row = self.db.execute(
            text(
                """
                SELECT p.id AS part_id,
                       p.part_number AS part_code,
                       p.part_name,
                       ci.id AS cost_item_id,
                       ci.calculation_name,
                       ci.material_cost,
                       ci.manufacturing_cost,
                       ci.overhead_cost,
                       ci.total_cost,
                       c.currency_code,
                       u.unit_code
                FROM part p
                JOIN cost_item ci ON ci.part_id = p.id
                LEFT JOIN currency c ON c.id = ci.currency_id
                LEFT JOIN unit u ON u.id = ci.unit_id
                WHERE p.id = :part_id
                ORDER BY ci.updated_at DESC, ci.id DESC
                LIMIT 1
                """
            ),
            {"part_id": part_id},
        ).mappings().first()
        if not row:
            return None

        material = float(row.get("material_cost") or 0.0)
        manu = float(row.get("manufacturing_cost") or 0.0)
        overhead = float(row.get("overhead_cost") or 0.0)
        total = float(row.get("total_cost") or 0.0)
        if total <= 0:
            total = material + manu + overhead

        def pct(v: float) -> float:
            return round((v / total * 100.0), 2) if total > 0 else 0.0

        return {
            "part_id": int(row["part_id"]),
            "part_code": row.get("part_code"),
            "part_name": row.get("part_name"),
            "cost_item_id": int(row["cost_item_id"]),
            "calculation_name": row.get("calculation_name"),
            "currency_code": row.get("currency_code"),
            "unit_code": row.get("unit_code"),
            "amounts": {
                "material_cost": material,
                "manufacturing_cost": manu,
                "overhead_cost": overhead,
                "total_cost": total,
            },
            "ratios_pct": {
                "material_cost": pct(material),
                "manufacturing_cost": pct(manu),
                "overhead_cost": pct(overhead),
            },
        }

    def _entity_lookup_by_message(self, message: str) -> dict[str, Any]:
        msg = (message or "").strip()
        if not msg:
            return {}
        msg_lower = msg.lower()
        wants_all_parts = bool(
            re.search(r"(所有|全部).{0,6}零件|零件.{0,8}(都列|列表|清单|列出)", msg)
        ) or ("all part" in msg_lower)
        wants_all_boms = ("所有bom" in msg_lower) or ("全部bom" in msg_lower) or ("bom清单" in msg_lower) or ("列出bom" in msg_lower) or ("all bom" in msg_lower)
        wants_all_cost_items = ("所有成本计算" in msg) or ("全部成本计算" in msg) or ("成本计算清单" in msg) or ("列出成本计算" in msg) or ("all cost item" in msg_lower) or ("all cost" in msg_lower)
        wants_all_materials = bool(re.search(r"(所有|全部).{0,4}(物料|材料)|(物料|材料).{0,6}(清单|列表|列出)", msg)) or ("all material" in msg_lower)
        wants_all_equipment = bool(re.search(r"(所有|全部).{0,4}设备|设备.{0,6}(清单|列表|列出)", msg)) or ("all equipment" in msg_lower)
        wants_all_regions = bool(re.search(r"(所有|全部).{0,4}区域|区域.{0,6}(清单|列表|列出)", msg)) or ("all region" in msg_lower)

        tokens = set(re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}", msg))
        tokens = {t for t in tokens if len(t) >= 2}
        msg_like = f"%{msg.lower()}%"
        out: dict[str, Any] = {}

        def _query(sql_text: str, params: dict[str, Any]) -> list[dict[str, Any]]:
            try:
                rows = self.db.execute(text(sql_text), params).mappings().all()
                return [dict(r) for r in rows]
            except Exception:
                return []

        # 零件
        part_rows = _query(
            """
            SELECT p.id, p.part_number AS part_code, p.part_name, p.lifecycle_status AS part_status, p.process_type AS lifecycle_stage
            FROM part p
            WHERE LOWER(p.part_number) LIKE :msg_like OR LOWER(p.part_name) LIKE :msg_like
            ORDER BY p.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if not part_rows and tokens:
            for tk in list(tokens)[:6]:
                part_rows = _query(
                    """
                    SELECT p.id, p.part_number AS part_code, p.part_name, p.lifecycle_status AS part_status, p.process_type AS lifecycle_stage
                    FROM part p
                    WHERE UPPER(p.part_number)=UPPER(:tk) OR LOWER(p.part_name) LIKE :name_like
                    ORDER BY p.id DESC
                    LIMIT 8
                    """,
                    {"tk": tk, "name_like": f"%{tk.lower()}%"},
                )
                if part_rows:
                    break
        if part_rows:
            out["parts"] = part_rows
        if wants_all_parts:
            part_all_rows = _query(
                """
                SELECT p.id, p.part_number AS part_code, p.part_name, p.lifecycle_status AS part_status, p.process_type AS lifecycle_stage
                FROM part p
                ORDER BY p.id ASC
                LIMIT 300
                """,
                {},
            )
            out["parts_all"] = part_all_rows

        # 成本计算
        cost_rows = _query(
            """
            SELECT ci.id, ci.calculation_name, p.part_number AS part_code, p.part_name,
                   ci.material_cost, ci.manufacturing_cost, ci.overhead_cost, ci.total_cost,
                   c.currency_code, u.unit_code, ci.updated_at
            FROM cost_item ci
            LEFT JOIN part p ON p.id = ci.part_id
            LEFT JOIN currency c ON c.id = ci.currency_id
            LEFT JOIN unit u ON u.id = ci.unit_id
            WHERE LOWER(ci.calculation_name) LIKE :msg_like
               OR LOWER(p.part_number) LIKE :msg_like
               OR LOWER(p.part_name) LIKE :msg_like
            ORDER BY ci.updated_at DESC, ci.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if cost_rows:
            out["cost_items"] = cost_rows

        # BOM
        bom_rows = _query(
            """
            SELECT b.id, b.bom_code, b.bom_name, p.part_number AS part_code, p.part_name, b.status
            FROM bom b
            LEFT JOIN part p ON p.id = b.part_id
            WHERE LOWER(b.bom_code) LIKE :msg_like
               OR LOWER(b.bom_name) LIKE :msg_like
               OR LOWER(p.part_number) LIKE :msg_like
               OR LOWER(p.part_name) LIKE :msg_like
            ORDER BY b.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if bom_rows:
            out["boms"] = bom_rows
        if wants_all_boms:
            out["boms_all"] = _query(
                """
                SELECT b.id, b.bom_code, b.bom_name, p.part_number AS part_code, p.part_name, b.status
                FROM bom b
                LEFT JOIN part p ON p.id = b.part_id
                ORDER BY b.id ASC
                LIMIT 300
                """,
                {},
            )

        bom_item_rows = _query(
            """
            SELECT bi.id, bi.bom_id, bi.item_number_snapshot, bi.item_name_snapshot, bi.quantity, bi.sort_no
            FROM bom_item bi
            WHERE LOWER(bi.item_number_snapshot) LIKE :msg_like
               OR LOWER(bi.item_name_snapshot) LIKE :msg_like
            ORDER BY bi.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if bom_item_rows:
            out["bom_items"] = bom_item_rows

        # 物料/设备
        mat_rows = _query(
            """
            SELECT m.id, m.material_code, m.material_name, m.density
            FROM material m
            WHERE LOWER(m.material_code) LIKE :msg_like OR LOWER(m.material_name) LIKE :msg_like
            ORDER BY m.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if mat_rows:
            out["materials"] = mat_rows
        if wants_all_materials:
            out["materials_all"] = _query(
                """
                SELECT m.id, m.material_code, m.material_name, m.density
                FROM material m
                ORDER BY m.id ASC
                LIMIT 300
                """,
                {},
            )

        eq_rows = _query(
            """
            SELECT e.id, e.equipment_code, e.equipment_name, e.equipment_type
            FROM equipment e
            WHERE LOWER(e.equipment_code) LIKE :msg_like OR LOWER(e.equipment_name) LIKE :msg_like
            ORDER BY e.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if eq_rows:
            out["equipment"] = eq_rows
        if wants_all_equipment:
            out["equipment_all"] = _query(
                """
                SELECT e.id, e.equipment_code, e.equipment_name, e.equipment_type
                FROM equipment e
                ORDER BY e.id ASC
                LIMIT 300
                """,
                {},
            )

        currency_rows = _query(
            """
            SELECT c.id, c.currency_code, c.currency_name, c.currency_symbol
            FROM currency c
            WHERE LOWER(c.currency_code) LIKE :msg_like
               OR LOWER(c.currency_name) LIKE :msg_like
               OR LOWER(c.currency_symbol) LIKE :msg_like
            ORDER BY c.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if currency_rows:
            out["currencies"] = currency_rows
        if ("所有币种" in msg) or ("全部币种" in msg) or ("币种列表" in msg) or ("currency list" in msg_lower):
            out["currencies_all"] = _query(
                """
                SELECT c.id, c.currency_code, c.currency_name, c.currency_symbol
                FROM currency c
                ORDER BY c.id ASC
                LIMIT 200
                """,
                {},
            )

        unit_rows = _query(
            """
            SELECT u.id, u.unit_code, u.unit_name, u.unit_category
            FROM unit u
            WHERE LOWER(u.unit_code) LIKE :msg_like
               OR LOWER(u.unit_name) LIKE :msg_like
               OR LOWER(u.unit_category) LIKE :msg_like
            ORDER BY u.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if unit_rows:
            out["units"] = unit_rows
        if ("所有单位" in msg) or ("全部单位" in msg) or ("单位列表" in msg) or ("unit list" in msg_lower):
            out["units_all"] = _query(
                """
                SELECT u.id, u.unit_code, u.unit_name, u.unit_category
                FROM unit u
                ORDER BY u.id ASC
                LIMIT 300
                """,
                {},
            )

        region_rows = _query(
            """
            SELECT r.id, r.region_code, r.region_name, r.region_type, r.level_no
            FROM region r
            WHERE LOWER(r.region_code) LIKE :msg_like
               OR LOWER(r.region_name) LIKE :msg_like
               OR LOWER(r.region_type) LIKE :msg_like
            ORDER BY r.id DESC
            LIMIT 8
            """,
            {"msg_like": msg_like},
        )
        if region_rows:
            out["regions"] = region_rows
        if wants_all_regions:
            out["regions_all"] = _query(
                """
                SELECT r.id, r.region_code, r.region_name, r.region_type
                FROM region r
                ORDER BY r.id ASC
                LIMIT 300
                """,
                {},
            )
        if wants_all_cost_items:
            out["cost_items_all"] = _query(
                """
                SELECT ci.id, ci.calculation_name, p.part_number AS part_code, p.part_name,
                       ci.total_cost, c.currency_code, u.unit_code
                FROM cost_item ci
                LEFT JOIN part p ON p.id = ci.part_id
                LEFT JOIN currency c ON c.id = ci.currency_id
                LEFT JOIN unit u ON u.id = ci.unit_id
                ORDER BY ci.id ASC
                LIMIT 300
                """,
                {},
            )

        return out

    def _direct_answer_by_message(self, clean_message: str, context_used: dict[str, Any]) -> str | None:
        msg = clean_message.strip()
        if not msg:
            return None
        hits = context_used.get("entity_hits") or {}
        workflow_import = context_used.get("workflow_import")
        msg_lower = msg.lower()
        wants_all_parts = bool(
            re.search(r"(所有|全部).{0,6}零件|零件.{0,8}(都列|列表|清单|列出)", msg)
        ) or ("all part" in msg_lower)
        wants_all_boms = ("所有bom" in msg_lower) or ("全部bom" in msg_lower) or ("bom清单" in msg_lower) or ("列出bom" in msg_lower) or ("all bom" in msg_lower)
        wants_all_cost_items = ("所有成本计算" in msg) or ("全部成本计算" in msg) or ("成本计算清单" in msg) or ("列出成本计算" in msg) or ("all cost item" in msg_lower) or ("all cost" in msg_lower)
        wants_all_materials = bool(re.search(r"(所有|全部).{0,4}(物料|材料)|(物料|材料).{0,6}(清单|列表|列出)", msg)) or ("all material" in msg_lower)
        wants_all_equipment = bool(re.search(r"(所有|全部).{0,4}设备|设备.{0,6}(清单|列表|列出)", msg)) or ("all equipment" in msg_lower)
        wants_all_regions = bool(re.search(r"(所有|全部).{0,4}区域|区域.{0,6}(清单|列表|列出)", msg)) or ("all region" in msg_lower)

        if workflow_import:
            created = workflow_import.get("created") or {}
            skipped = workflow_import.get("skipped") or {}
            errors = workflow_import.get("errors") or []
            created_text = "，".join([f"{k}:{v}" for k, v in created.items()]) or "无"
            skipped_text = "，".join([f"{k}:{v}" for k, v in skipped.items()]) or "无"
            error_text = "\n".join([f"- {x}" for x in errors]) if errors else "- 无"
            return (
                "已完成 AI 结构化数据录入。\n\n"
                f"新建记录：{created_text}\n"
                f"跳过已存在：{skipped_text}\n\n"
                "异常/提示：\n"
                f"{error_text}\n\n"
                "已刷新运行时数据快照，你可以继续让我查询零件、BOM或成本结果。"
            )

        if wants_all_parts:
            rows = hits.get("parts_all") or []
            if not rows:
                return "当前未查询到零件数据。"
            lines = []
            for i, r in enumerate(rows[:300], start=1):
                lines.append(f"{i}. {r.get('part_name')} ({r.get('part_code')})")
            return f"当前零件共 {len(rows)} 条，名称如下：\n" + "\n".join(lines)

        if ("所有币种" in msg) or ("全部币种" in msg) or ("币种列表" in msg) or ("currency list" in msg_lower):
            rows = hits.get("currencies_all") or []
            if not rows:
                return "当前未查询到币种数据。"
            lines = [f"{i}. {r.get('currency_name')} ({r.get('currency_code')})" for i, r in enumerate(rows, start=1)]
            return f"当前币种共 {len(rows)} 条：\n" + "\n".join(lines)

        if ("所有单位" in msg) or ("全部单位" in msg) or ("单位列表" in msg) or ("unit list" in msg_lower):
            rows = hits.get("units_all") or []
            if not rows:
                return "当前未查询到单位数据。"
            lines = [f"{i}. {r.get('unit_name')} ({r.get('unit_code')})" for i, r in enumerate(rows, start=1)]
            return f"当前单位共 {len(rows)} 条：\n" + "\n".join(lines)

        if wants_all_boms:
            rows = hits.get("boms_all") or []
            if not rows:
                return "当前未查询到BOM数据。"
            lines = [f"{i}. {r.get('bom_name')} ({r.get('bom_code')}) - 父件:{r.get('part_name')}" for i, r in enumerate(rows, start=1)]
            return f"当前BOM共 {len(rows)} 条：\n" + "\n".join(lines)

        if wants_all_cost_items:
            rows = hits.get("cost_items_all") or []
            if not rows:
                return "当前未查询到成本计算数据。"
            lines = [
                f"{i}. {r.get('calculation_name')} | {r.get('part_name')} ({r.get('part_code')}) | 总成本:{r.get('total_cost')} {r.get('currency_code')}/{r.get('unit_code')}"
                for i, r in enumerate(rows, start=1)
            ]
            return f"当前成本计算共 {len(rows)} 条：\n" + "\n".join(lines)

        if wants_all_materials:
            rows = hits.get("materials_all") or []
            if not rows:
                return "当前未查询到物料数据。"
            lines = [f"{i}. {r.get('material_name')} ({r.get('material_code')})" for i, r in enumerate(rows, start=1)]
            return f"当前物料共 {len(rows)} 条：\n" + "\n".join(lines)

        if wants_all_equipment:
            rows = hits.get("equipment_all") or []
            if not rows:
                return "当前未查询到设备数据。"
            lines = [f"{i}. {r.get('equipment_name')} ({r.get('equipment_code')})" for i, r in enumerate(rows, start=1)]
            return f"当前设备共 {len(rows)} 条：\n" + "\n".join(lines)

        if wants_all_regions:
            rows = hits.get("regions_all") or []
            if not rows:
                return "当前未查询到区域数据。"
            lines = [f"{i}. {r.get('region_name')} ({r.get('region_code')})" for i, r in enumerate(rows, start=1)]
            return f"当前区域共 {len(rows)} 条：\n" + "\n".join(lines)

        return None

    def _fallback_answer(
        self,
        clean_message: str,
        context_used: dict[str, Any],
        no_key: bool = False,
    ) -> dict[str, Any]:
        header = "当前未启用远程大模型，已使用本地应急助手回答。" if no_key else "当前使用本地应急助手回答。"
        runtime = context_used.get("runtime_snapshot", {}).get("table_counts", {})
        explicit_lookup = context_used.get("explicit_part_cost_lookup")
        if explicit_lookup:
            amounts = explicit_lookup.get("amounts", {})
            ratios = explicit_lookup.get("ratios_pct", {})
            currency_code = explicit_lookup.get("currency_code") or "-"
            unit_code = explicit_lookup.get("unit_code") or "-"
            answer = (
                f"{header}\n\n"
                f"已为你定位到零件：{explicit_lookup.get('part_name')} ({explicit_lookup.get('part_code')})\n"
                f"成本计算：{explicit_lookup.get('calculation_name')} (ID={explicit_lookup.get('cost_item_id')})\n\n"
                f"总成本：{amounts.get('total_cost', 0):.4f} {currency_code}/{unit_code}\n"
                f"- 材料成本：{amounts.get('material_cost', 0):.4f}，占比 {ratios.get('material_cost', 0):.2f}%\n"
                f"- 制造成本：{amounts.get('manufacturing_cost', 0):.4f}，占比 {ratios.get('manufacturing_cost', 0):.2f}%\n"
                f"- 间接费用：{amounts.get('overhead_cost', 0):.4f}，占比 {ratios.get('overhead_cost', 0):.2f}%\n"
            )
            return {
                "answer": answer,
                "suggestions": self._suggestions_by_question(clean_message),
                "model": settings.llm_model,
                "provider_style": settings.llm_api_style,
                "context_used": context_used,
            }

        answer = (
            f"{header}\n\n"
            f"你的问题：{clean_message}\n\n"
            "我可以先给你系统现状：\n"
            f"- 零件表记录数: {runtime.get('part', 0)}\n"
            f"- BOM头记录数: {runtime.get('bom', 0)}\n"
            f"- BOM子项记录数: {runtime.get('bom_item', 0)}\n"
            f"- 成本计算记录数: {runtime.get('cost_item', 0)}\n\n"
            "如果你配置好 LLM 环境变量，我可以提供更完整的操作指导、数据地图解释和成本优化建议。"
        )
        return {
            "answer": answer,
            "suggestions": self._suggestions_by_question(clean_message),
            "model": settings.llm_model,
            "provider_style": settings.llm_api_style,
            "context_used": context_used,
        }

    def _suggestions_by_question(self, clean_message: str) -> list[str]:
        q = clean_message.lower()
        if "成本" in clean_message or "cost" in q:
            return [
                "请分析当前零件成本中材料/制造/间接费用占比",
                "请给出3条降低材料成本的可执行建议",
                "请解释制造成本I和制造成本II分别代表什么",
            ]
        if "元数据" in clean_message or "字段" in clean_message or "表" in clean_message:
            return [
                "请解释 part、bom、cost_item 三张表的关系",
                "请列出成本计算相关主外键",
                "请给出数据治理中主数据与事务数据的边界说明",
            ]
        return [
            "零件成本计算的完整操作路径是什么？",
            "请解释首页各指标代表的业务含义",
            "我在当前页面下一步应该做什么？",
        ]

    def _effective_api_key(self, runtime_api_key: str | None = None) -> str | None:
        return (
            (runtime_api_key or "").strip()
            or settings.llm_api_key
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("IDME_LLM_API_KEY")
        )


def datetime_now_text() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
