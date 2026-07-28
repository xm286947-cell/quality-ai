from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest

from business_agent.input.parser import InputParser
from business_agent.knowledge.adapter import KnowledgeContractAdapter
from business_agent.models import AgentProfile, RuntimeContext, RuntimeRequest, WorkflowNode

ROOT = Path(__file__).resolve().parents[1]


def _make_excel(path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["查询编号", "问题描述"])
    ws.append(["CASE001", "CAN接收拥堵导致软件保护重启"])
    ws.append(["CASE002", "通信异常导致设备离线"])
    wb.save(path)


def test_parse_input_before_knowledge(tmp_path: Path) -> None:
    excel = tmp_path / "cases.xlsx"
    _make_excel(excel)
    profile = AgentProfile("repeat_case", "REPEAT_CASE", "1.1", "", ())
    request = RuntimeRequest("repeat_case", {"input": str(excel), "top_k": 3}, request_id="WFV1-001")
    context = RuntimeContext(request, profile)
    parse_node = WorkflowNode("parse_input", "python_handler", "input.parse")
    parsed = InputParser(ROOT).parse(context, parse_node)
    context.data.update(parsed["context_updates"])

    assert len(context.data["cases"]) == 2
    assert context.data["cases"][0]["query_text"] == "CAN接收拥堵导致软件保护重启"

    knowledge_node = WorkflowNode(
        "knowledge_search",
        "python_handler",
        "knowledge.search",
        config={"provider": "mock", "service_id": "repeat_case_service"},
    )
    result = KnowledgeContractAdapter(ROOT).search(context, knowledge_node)
    requests = result["context_updates"]["knowledge_requests"]
    assert len(requests) == 2
    assert requests[0]["query"] == {"text": "CAN接收拥堵导致软件保护重启"}
    assert requests[1]["query"] == {"text": "通信异常导致设备离线"}


def test_knowledge_fails_when_parse_not_run() -> None:
    profile = AgentProfile("repeat_case", "REPEAT_CASE", "1.1", "", ())
    context = RuntimeContext(RuntimeRequest("repeat_case", {"input": "input/new_cases.xlsx"}), profile)
    node = WorkflowNode("knowledge_search", "python_handler", "knowledge.search", config={"provider": "mock"})
    with pytest.raises(ValueError, match="parse_input"):
        KnowledgeContractAdapter(ROOT).search(context, node)
