from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_agent.models import RuntimeContext, WorkflowNode
from parser.query_excel_parser import QueryExcelParser
from .models import CaseInput


class InputParser:
    """Parse raw runtime input into stable CaseInput objects before knowledge access."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()

    def parse(self, context: RuntimeContext, node: WorkflowNode) -> dict[str, Any]:
        inputs = context.request.inputs
        source_value = inputs.get("input")
        if not source_value:
            raise ValueError("INVALID_INPUT: input is required")
        source = Path(str(source_value))
        if not source.is_absolute():
            source = self.project_root / source
        if not source.exists():
            raise FileNotFoundError(f"INVALID_INPUT: input file not found: {source}")

        suffix = source.suffix.lower()
        if suffix in {".xlsx", ".xlsm"}:
            cases, parse_summary = self._parse_excel(source, context.request.request_id)
        elif suffix == ".json":
            cases, parse_summary = self._parse_json(source)
        else:
            raise ValueError(f"INVALID_INPUT: unsupported input format: {suffix}")

        selected_query_id = str(inputs.get("query_id") or "").strip()
        if selected_query_id:
            cases = [case for case in cases if case.case_id == selected_query_id]
            if not cases:
                raise ValueError(f"INVALID_INPUT: query_id not found: {selected_query_id}")

        invalid = [case.case_id for case in cases if not case.query_text.strip()]
        if invalid:
            raise ValueError(f"INVALID_INPUT: empty query_text for cases: {', '.join(invalid)}")
        if not cases:
            raise ValueError("INVALID_INPUT: no valid cases parsed")

        case_dicts = [case.to_dict() for case in cases]
        return {
            "summary": {
                "case_count": len(case_dicts),
                "source": str(source),
                "format": suffix.lstrip("."),
            },
            "output": {"cases": case_dicts, "parse_summary": parse_summary},
            "context_updates": {"cases": case_dicts, "parse_summary": parse_summary},
        }

    def _parse_excel(self, source: Path, request_id: str) -> tuple[list[CaseInput], dict[str, Any]]:
        parser = QueryExcelParser(self.project_root / "config" / "query_field_mapping.yaml")
        out_dir = self.project_root / "output" / "agent_runs" / request_id / "parsed_queries"
        records, summary = parser.parse(source, out_dir)
        cases: list[CaseInput] = []
        for record in records:
            if record.get("parse_status") == "QUERY_PARSE_FAILED":
                continue
            mapped = dict(record.get("mapped_fields") or {})
            description = str(mapped.get("problem_description") or "").strip()
            title = str(mapped.get("title") or mapped.get("problem_title") or "").strip()
            query_text = self._build_query_text(title, description)
            cases.append(
                CaseInput(
                    case_id=str(record.get("query_id") or f"ROW-{record.get('excel_row', '')}"),
                    title=title,
                    description=description,
                    query_text=query_text,
                    metadata={
                        "source_excel": record.get("source_excel"),
                        "sheet_name": record.get("sheet_name"),
                        "excel_row": record.get("excel_row"),
                        "mapped_fields": mapped,
                        "parse_status": record.get("parse_status"),
                        "parse_warnings": record.get("parse_warnings") or [],
                    },
                )
            )
        return cases, summary.to_dict()

    def _parse_json(self, source: Path) -> tuple[list[CaseInput], dict[str, Any]]:
        payload = json.loads(source.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("cases", [])
        if not isinstance(rows, list):
            raise ValueError("INVALID_INPUT: JSON must be a list or contain cases[]")
        cases: list[CaseInput] = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            case_id = str(row.get("case_id") or row.get("query_id") or f"CASE-{index:04d}")
            title = str(row.get("title") or "").strip()
            description = str(row.get("description") or row.get("problem_description") or "").strip()
            query_text = str(row.get("query_text") or self._build_query_text(title, description)).strip()
            cases.append(CaseInput(case_id, title, description, query_text, dict(row.get("metadata") or {})))
        return cases, {"source": str(source), "total": len(rows), "success": len(cases)}

    @staticmethod
    def _build_query_text(title: str, description: str) -> str:
        if title and description and title not in description:
            return f"{title}\n{description}".strip()
        return (description or title).strip()
