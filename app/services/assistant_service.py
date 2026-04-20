import json
from pathlib import Path
from typing import Any

import requests
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


class AssistantService:
    def __init__(self, db: Session):
        self.db = db

    def capabilities(self) -> dict[str, Any]:
        return {
            "llm_enabled": bool(settings.llm_enabled),
            "llm_configured": bool(settings.llm_api_key),
            "provider_style": settings.llm_api_style,
            "model": settings.llm_model,
            "features": [
                "系统操作指南问答",
                "元数据与数据地图检索解释",
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
    ) -> dict[str, Any]:
        clean_message = message.strip()
        if not clean_message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="消息不能为空")

        context_data = dict(context or {})
        metadata_context = self._metadata_context(clean_message)
        runtime_context = self._runtime_snapshot() if use_runtime_snapshot else {}
        part_context = self._part_context(context_data)

        context_used = {
            "ui_context": context_data,
            "runtime_snapshot": runtime_context,
            "part_context": part_context,
            "metadata_tables": metadata_context.get("table_names", []),
        }

        if not settings.llm_enabled:
            return self._fallback_answer(clean_message, context_used)

        if not settings.llm_api_key:
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
        )
        return {
            "answer": answer,
            "suggestions": self._suggestions_by_question(clean_message),
            "model": settings.llm_model,
            "provider_style": settings.llm_api_style,
            "context_used": context_used,
        }

    def _invoke_llm(self, system_prompt: str, history: list[dict[str, str]], user_prompt: str) -> str:
        style = (settings.llm_api_style or "openai").lower()
        base_url = settings.llm_base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
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
            f"当前上下文(JSON):\n{json.dumps(context_used, ensure_ascii=False)}\n\n"
            f"系统操作指南(JSON):\n{json.dumps(ops_guide, ensure_ascii=False)}\n\n"
            f"元数据摘录(JSON):\n{json.dumps(metadata_context, ensure_ascii=False)}\n\n"
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
                    }
                )
            slim_tables.append(
                {
                    "table_name": t.get("table_name"),
                    "table_display_name": t.get("table_display_name"),
                    "table_description": t.get("table_description"),
                    "fields": slim_fields,
                }
            )
        return {"tables": slim_tables, "table_names": [t.get("table_name") for t in slim_tables]}

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

        return out

    def _fallback_answer(
        self,
        clean_message: str,
        context_used: dict[str, Any],
        no_key: bool = False,
    ) -> dict[str, Any]:
        header = "当前未启用远程大模型，已使用本地应急助手回答。" if no_key else "当前使用本地应急助手回答。"
        runtime = context_used.get("runtime_snapshot", {}).get("table_counts", {})
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


def datetime_now_text() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
