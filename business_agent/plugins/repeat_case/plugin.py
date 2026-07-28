from __future__ import annotations

from pathlib import Path

from business_agent.adapters.repeat_case_adapter import RepeatCaseAdapter
from business_agent.knowledge.adapter import KnowledgeContractAdapter
from business_agent.input.parser import InputParser


def register(registry, project_root: str | Path) -> None:
    input_parser = InputParser(project_root)
    knowledge = KnowledgeContractAdapter(project_root)
    adapter = RepeatCaseAdapter(project_root)
    if not registry.contains("input.parse"):
        registry.register("input.parse", input_parser.parse)
    if not registry.contains("knowledge.search"):
        registry.register("knowledge.search", knowledge.search)
    if not registry.contains("repeat_case.run_analysis"):
        registry.register("repeat_case.run_analysis", adapter.run_analysis)
