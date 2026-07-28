from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from business_agent.knowledge.adapter import KnowledgeContractAdapter
from business_agent.models import AgentProfile, RuntimeContext, RuntimeRequest, WorkflowNode


class _KnowledgeHandler(BaseHTTPRequestHandler):
    received: list[dict] = []

    def log_message(self, *_args):
        return

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(size).decode("utf-8"))
        self.__class__.received.append(payload)
        body = json.dumps({
            "contract_version": "V1.0",
            "request_id": payload["request_id"],
            "status": "success",
            "items": [{
                "item_id": "CASE-HISTORY-001",
                "score": 0.91,
                "content": {"title": "历史相似问题"},
                "evidence": [{"evidence_id": "E-001", "source": "history"}],
            }],
            "total": 1,
            "provider": "test-http",
            "elapsed_ms": 1,
            "metadata": {},
        }, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def test_repeat_case_knowledge_uses_real_http(tmp_path: Path):
    _KnowledgeHandler.received = []
    server = HTTPServer(("127.0.0.1", 0), _KnowledgeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        profile = AgentProfile("repeat_case", "REPEAT_CASE", "1.1", "", ())
        request = RuntimeRequest(
            "repeat_case",
            {"top_k": 3},
            request_id="HTTP-CONTRACT-001",
            options={"knowledge": {"provider": "http", "base_url": f"http://127.0.0.1:{server.server_port}"}},
        )
        context = RuntimeContext(request, profile, data={"cases": [{
            "case_id": "Q1",
            "query_text": "CAN接收拥堵导致软件重启",
        }]})
        node = WorkflowNode("knowledge_search", "python_handler", "knowledge.search", config={
            "provider": "http", "service_id": "repeat_case_service", "endpoint": "/v1/knowledge/query"
        })
        result = KnowledgeContractAdapter(tmp_path).search(context, node)
        assert result["summary"]["recall_count"] == 1
        assert len(_KnowledgeHandler.received) == 1
        sent = _KnowledgeHandler.received[0]
        assert sent["query"] == {"text": "CAN接收拥堵导致软件重启"}
        assert sent["service_id"] == "repeat_case_service"
        assert sent["caller"]["agent_id"] == "repeat_case"
    finally:
        server.shutdown()
        thread.join(timeout=2)
