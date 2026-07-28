from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from builder.m2_runner import run_m2
from builder.m3_runner import run_m3
from builder.m4_runner import run_m4
from builder.m5_runner import run_m5
from builder.m6_runner import run_m6
from builder.m7_runner import run_m7
from builder.m71_query_runner import run_m71_query
from builder.m72_normalizer_runner import run_m72_normalizer
from builder.m72_ai_runner import run_m72_ai
from builder.m72_standard_builder_runner import run_m72_standard_builder
from builder.query_enricher import run_m72_pipeline
from builder.m73_profile_runner import run_m73_profile
from builder.m73_retriever_runner import run_m73_retrieve
from builder.m81_candidate_runner import run_m81_load
from builder.m82_similarity_runner import run_m82_similarity
from builder.m83_solution_runner import run_m83_solution
from builder.m84_repeat_runner import run_m84_decision
from builder.m85_delivery_runner import run_m85_delivery
from builder.pipeline_runner import run_all
from builder.analysis_pipeline_runner import run_analysis_pipeline
from builder.local_batch_runner import run_local_batch
from builder.validators import SchemaValidationError, validate_json_file
from business_agent.models import RuntimeRequest
from business_agent.runtime.runtime import BusinessAgentRuntime


ROOT = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="REPEAT_CASE_ENGINE V2.3 M8.5")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-case", help="校验Standard Case JSON")
    validate.add_argument("json_file")
    validate.add_argument("--schema", default=str(ROOT / "schema/standard_case.schema.json"))

    m2 = subparsers.add_parser("run-m2", help="运行Excel解析与报告匹配")
    m2.add_argument("--excel", default=None)
    m2.add_argument("--reports-dir", default=None)

    m3 = subparsers.add_parser("run-m3", help="解析PDF并更新raw_evidence")
    m3.add_argument("--case-id", default=None)

    m4 = subparsers.add_parser("run-m4", help="生成纯事实Standard Case")
    m4.add_argument("--case-id", default=None)

    m5 = subparsers.add_parser("run-m5", help="AI增强Standard Case")
    m5.add_argument("--case-id", default=None)
    m5.add_argument("--mock", action="store_true")
    m5.add_argument("--overwrite", action="store_true")

    m6 = subparsers.add_parser("run-m6", help="构建检索文档、Embedding、Manifest和索引")
    m6.add_argument("--case-id", default=None)
    m6.add_argument("--overwrite", action="store_true")

    m71 = subparsers.add_parser("run-m7-query", help="解析new_cases.xlsx并生成Raw Query")
    m71.add_argument("--input", default=None, help="待分析问题Excel，默认input/new_cases.xlsx")
    m71.add_argument("--overwrite", action="store_true", help="覆盖已有Raw Query JSON")

    m72n = subparsers.add_parser("run-m72-normalize", help="将Raw Query标准化为Normalized Query")
    m72n.add_argument("--query-id", default=None)
    m72n.add_argument("--overwrite", action="store_true")

    m72a = subparsers.add_parser("run-m72-ai", help="将Normalized Query进行AI增强")
    m72a.add_argument("--query-id", default=None)
    m72a.add_argument("--overwrite", action="store_true")
    m72a.add_argument("--mock", action="store_true", help="使用本地Mock响应")
    m72a.add_argument("--skip-ai", action="store_true", help="跳过AI并生成降级Enriched Query")

    m72b = subparsers.add_parser("run-m72-build", help="将Enriched Query组装为Standard Query")
    m72b.add_argument("--query-id", default=None)
    m72b.add_argument("--overwrite", action="store_true")

    m72 = subparsers.add_parser("run-m72", help="运行Query Enricher完整Pipeline")
    m72.add_argument("--query-id", default=None, help="仅处理指定Query ID")
    m72.add_argument("--overwrite", action="store_true", help="覆盖各阶段已有输出")
    m72.add_argument("--mock", action="store_true", help="AI阶段使用本地Mock响应")
    m72.add_argument("--skip-ai", action="store_true", help="跳过AI并降级构建Standard Query")
    m72.add_argument(
        "--from-stage",
        choices=["normalize", "ai", "build"],
        default="normalize",
        help="从指定阶段开始执行并继续到Builder",
    )

    m73p = subparsers.add_parser("run-m73-profile", help="从Standard Query生成Retrieval Profile")
    m73p.add_argument("--query-id", default=None)
    m73p.add_argument("--overwrite", action="store_true")

    m73r = subparsers.add_parser("run-m73-retrieve", help="使用Retrieval Profile调用现有Retriever")
    m73r.add_argument("--query-id", default=None)
    m73r.add_argument("--top-k", type=int, default=None)
    m73r.add_argument("--overwrite", action="store_true")

    m81 = subparsers.add_parser("run-m81-load", help="加载候选案例并生成Analysis Context")
    m81.add_argument("--query-id", default=None)
    m81.add_argument("--top-k", type=int, default=None)
    m81.add_argument("--overwrite", action="store_true")

    m82 = subparsers.add_parser("run-m82-similarity", help="分析新问题与候选历史案例的多维相似性")
    m82.add_argument("--query-id", default=None)
    m82.add_argument("--case-id", default=None)
    m82.add_argument("--overwrite", action="store_true")
    m82.add_argument("--mock", action="store_true", help="使用本地Mock响应")
    m82.add_argument("--skip-ai", action="store_true", help="跳过AI并生成UNKNOWN降级结果")

    m83 = subparsers.add_parser("run-m83-solution", help="分析历史案例解决方案有效性与复用价值")
    m83.add_argument("--query-id", default=None)
    m83.add_argument("--case-id", default=None)
    m83.add_argument("--overwrite", action="store_true")
    m83.add_argument("--mock", action="store_true", help="使用本地Mock响应")
    m83.add_argument("--skip-ai", action="store_true", help="跳过AI并生成UNKNOWN降级结果")

    m84 = subparsers.add_parser("run-m84-decision", help="综合相似性与解决方案分析，生成重复问题判定")
    m84.add_argument("--query-id", default=None)
    m84.add_argument("--overwrite", action="store_true")
    m84.add_argument("--mock", action="store_true", help="使用本地Mock响应")
    m84.add_argument("--skip-ai", action="store_true", help="跳过AI并生成证据不足降级结果")

    m85 = subparsers.add_parser("run-m85-delivery", help="从RepeatAnalysis生成正式Report JSON与Markdown交付件")
    m85.add_argument("--query-id", default=None)
    m85.add_argument("--overwrite", action="store_true")

    m7 = subparsers.add_parser("run-m7", help="检索相似历史案例")
    m7.add_argument("--text", required=True, help="新问题描述")
    m7.add_argument("--top-k", type=int, default=None)
    m7.add_argument("--ipmt", default="")
    m7.add_argument("--spdt", default="")
    m7.add_argument("--department", default="")
    m7.add_argument("--product", default="")
    m7.add_argument("--domain", default="")
    m7.add_argument("--cause-level1", default="")
    m7.add_argument("--cause-level2", default="")
    m7.add_argument("--cause-description", default="", help="原因描述、TRC、根因或失效机制")
    m7.add_argument("--solution", default="", help="纠正、预防或可复用解决措施")

    analysis_cmd = subparsers.add_parser("run-analysis", help="端到端运行新问题重复案例分析链路")
    analysis_cmd.add_argument("--input", default=None, help="待分析问题Excel，默认input/new_cases.xlsx")
    analysis_cmd.add_argument("--query-id", default=None, help="仅处理指定Query ID")
    analysis_cmd.add_argument("--from-stage", choices=["parse", "enrich", "profile", "retrieve", "load", "similarity", "solution", "decision", "delivery"], default="parse")
    analysis_cmd.add_argument("--top-k", type=int, default=None)
    analysis_cmd.add_argument("--overwrite", action="store_true")
    analysis_cmd.add_argument("--mock", action="store_true", help="AI阶段使用本地Mock响应")
    analysis_cmd.add_argument("--skip-ai", action="store_true", help="跳过AI并生成降级结果")

    batch = subparsers.add_parser("run-batch", help="本地真实案例批量运行、断点续跑与诊断")
    batch.add_argument("--input", default=None, help="待分析问题Excel，默认input/new_cases.xlsx")
    batch.add_argument("--run-id", default=None, help="指定Run ID；续跑时必填")
    batch.add_argument("--resume", action="store_true", help="续跑已有Run")
    batch.add_argument("--retry-failed", action="store_true", help="续跑时仅重跑失败Query")
    batch.add_argument("--top-k", type=int, default=None)
    batch.add_argument("--no-overwrite", action="store_true", help="不覆盖阶段已有结果")
    batch.add_argument("--mock", action="store_true", help="AI阶段使用本地Mock")
    batch.add_argument("--skip-ai", action="store_true", help="跳过AI并生成降级结果")
    batch.add_argument("--include-sensitive-debug", action="store_true", help="在Run目录复制敏感中间数据；默认关闭")

    all_cmd = subparsers.add_parser("run-all", help="运行M2至M6")
    all_cmd.add_argument("--excel", default=None)
    all_cmd.add_argument("--reports-dir", default=None)
    all_cmd.add_argument("--with-ai", action="store_true")
    all_cmd.add_argument("--mock-ai", action="store_true")
    all_cmd.add_argument("--overwrite-ai", action="store_true")
    all_cmd.add_argument("--with-index", action="store_true")
    all_cmd.add_argument("--overwrite-index", action="store_true")

    list_agents = subparsers.add_parser("list-agents", help="列出BUSINESS_AGENT_ENGINE已注册Agent")

    run_agent = subparsers.add_parser("run-agent", help="通过统一Business Agent Runtime运行Agent")
    run_agent.add_argument("--agent", required=True, help="Agent ID，例如repeat_case")
    run_agent.add_argument("--request-id", default="")
    run_agent.add_argument("--input-json", default=None, help="运行输入JSON文件")
    run_agent.add_argument("--input", default=None, help="兼容REPEAT_CASE：待分析问题Excel")
    run_agent.add_argument("--query-id", default=None)
    run_agent.add_argument("--from-stage", default=None)
    run_agent.add_argument("--top-k", type=int, default=None)
    run_agent.add_argument("--overwrite", action="store_true")
    run_agent.add_argument("--mock", action="store_true")
    run_agent.add_argument("--skip-ai", action="store_true")

    return parser


def _print(result: dict) -> int:
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "validate-case":
        try:
            validate_json_file(args.json_file, args.schema)
        except FileNotFoundError as exc:
            print(f"[ERROR] 文件不存在: {exc}", file=sys.stderr)
            return 2
        except SchemaValidationError as exc:
            print(f"[INVALID]\n{exc}", file=sys.stderr)
            return 1
        print("[VALID] Standard Case校验通过")
        return 0

    try:
        if args.command == "run-m2":
            return _print(run_m2(ROOT, excel_path=args.excel, reports_dir=args.reports_dir))
        if args.command == "run-m3":
            return _print(run_m3(ROOT, case_id=args.case_id))
        if args.command == "run-m4":
            return _print(run_m4(ROOT, case_id=args.case_id))
        if args.command == "run-m5":
            return _print(run_m5(ROOT, case_id=args.case_id, mock=args.mock, overwrite=args.overwrite))
        if args.command == "run-m6":
            return _print(run_m6(ROOT, case_id=args.case_id, overwrite=args.overwrite))
        if args.command == "run-m7-query":
            return _print(run_m71_query(ROOT, input_path=args.input, overwrite=args.overwrite))
        if args.command == "run-m72-normalize":
            return _print(run_m72_normalizer(ROOT, query_id=args.query_id, overwrite=args.overwrite))
        if args.command == "run-m72-ai":
            return _print(run_m72_ai(ROOT, query_id=args.query_id, overwrite=args.overwrite, mock=args.mock, skip_ai=args.skip_ai))
        if args.command == "run-m72-build":
            return _print(run_m72_standard_builder(ROOT, query_id=args.query_id, overwrite=args.overwrite))
        if args.command == "run-m72":
            return _print(run_m72_pipeline(
                ROOT,
                query_id=args.query_id,
                overwrite=args.overwrite,
                mock=args.mock,
                skip_ai=args.skip_ai,
                from_stage=args.from_stage,
            ))
        if args.command == "run-m73-profile":
            return _print(run_m73_profile(ROOT, query_id=args.query_id, overwrite=args.overwrite))
        if args.command == "run-m73-retrieve":
            return _print(run_m73_retrieve(ROOT, query_id=args.query_id, top_k=args.top_k, overwrite=args.overwrite))
        if args.command == "run-m81-load":
            return _print(run_m81_load(ROOT, query_id=args.query_id, top_k=args.top_k, overwrite=args.overwrite))
        if args.command == "run-m82-similarity":
            return _print(run_m82_similarity(
                ROOT, query_id=args.query_id, case_id=args.case_id,
                overwrite=args.overwrite, mock=args.mock, skip_ai=args.skip_ai,
            ))
        if args.command == "run-m83-solution":
            return _print(run_m83_solution(
                ROOT, query_id=args.query_id, case_id=args.case_id,
                overwrite=args.overwrite, mock=args.mock, skip_ai=args.skip_ai,
            ))
        if args.command == "run-m84-decision":
            return _print(run_m84_decision(
                ROOT, query_id=args.query_id, overwrite=args.overwrite,
                mock=args.mock, skip_ai=args.skip_ai,
            ))
        if args.command == "run-m85-delivery":
            return _print(run_m85_delivery(ROOT, query_id=args.query_id, overwrite=args.overwrite))
        if args.command == "run-m7":
            return _print(run_m7(
                ROOT,
                query_text=args.text,
                top_k=args.top_k,
                ipmt=args.ipmt,
                spdt=args.spdt,
                responsible_department_level2=args.department,
                product=args.product,
                domain=args.domain,
                cause_level1=args.cause_level1,
                cause_level2=args.cause_level2,
                cause_description=args.cause_description,
                solution=args.solution,
            ))
        if args.command == "run-analysis":
            return _print(run_analysis_pipeline(
                ROOT, input_path=args.input, query_id=args.query_id,
                from_stage=args.from_stage, top_k=args.top_k,
                overwrite=args.overwrite, mock=args.mock, skip_ai=args.skip_ai,
            ))
        if args.command == "run-batch":
            return _print(run_local_batch(
                ROOT,
                input_path=args.input,
                run_id=args.run_id,
                resume=args.resume,
                retry_failed=args.retry_failed,
                top_k=args.top_k,
                overwrite=not args.no_overwrite,
                mock=args.mock,
                skip_ai=args.skip_ai,
                include_sensitive_debug=args.include_sensitive_debug,
            ))
        if args.command == "run-all":
            return _print(run_all(
                ROOT,
                excel_path=args.excel,
                reports_dir=args.reports_dir,
                with_ai=args.with_ai,
                mock_ai=args.mock_ai,
                overwrite_ai=args.overwrite_ai,
                with_index=args.with_index,
                overwrite_index=args.overwrite_index,
            ))
        if args.command == "list-agents":
            return _print({"agents": BusinessAgentRuntime(ROOT).list_agents()})
        if args.command == "run-agent":
            inputs = {}
            if args.input_json:
                inputs = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
                if not isinstance(inputs, dict):
                    raise ValueError("input-json根节点必须是对象")
            cli_inputs = {
                "input": args.input,
                "query_id": args.query_id,
                "from_stage": args.from_stage,
                "top_k": args.top_k,
            }
            inputs.update({key: value for key, value in cli_inputs.items() if value is not None})
            if args.overwrite:
                inputs["overwrite"] = True
            if args.mock:
                inputs["mock"] = True
            if args.skip_ai:
                inputs["skip_ai"] = True
            runtime_result = BusinessAgentRuntime(ROOT).run(RuntimeRequest(
                agent_id=args.agent, inputs=inputs, request_id=args.request_id,
            ))
            return _print({
                "request_id": runtime_result.request_id,
                "agent_id": runtime_result.agent_id,
                "agent_version": runtime_result.agent_version,
                "status": runtime_result.status,
                "output": runtime_result.output,
                "trace_path": runtime_result.trace_path,
            })
    except Exception as exc:
        print(f"[ERROR] {args.command}运行失败: {exc}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
