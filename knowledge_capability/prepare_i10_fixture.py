from __future__ import annotations

import json
from pathlib import Path

from builder.embedding_client import LocalHashEmbeddingClient


def prepare(project_root: str | Path | None = None) -> dict[str, int]:
    root = Path(project_root or Path(__file__).resolve().parent).resolve()
    index_dir = root / "knowledge" / "index"
    docs_dir = root / "knowledge" / "retrieval_docs"
    embeddings_dir = root / "knowledge" / "embeddings"
    for directory in (index_dir, docs_dir, embeddings_dir):
        directory.mkdir(parents=True, exist_ok=True)

    client = LocalHashEmbeddingClient(dimensions=256, model="local-hash-v1")
    samples = [
        ("CASE-I10-001", "CAN报文过多导致接收处理拥堵，软件触发保护并重启", "CAN接收拥堵导致软件保护重启"),
        ("CASE-I10-002", "界面按钮颜色显示异常，刷新后恢复", "界面显示异常"),
    ]
    records = []
    for case_id, text, title in samples:
        document = {
            "document_id": f"DOC-{case_id}",
            "case_id": case_id,
            "itr_id": "",
            "source_case_path": "",
            "organization": {"ipmt": "", "spdt": "", "responsible_department_level2": ""},
            "classification": {"cause_level1": "软件设计", "cause_level2": "资源处理", "source": "I10"},
            "filters": {"product": "", "domain": ""},
            "title": title,
            "text": text,
            "tags": ["CAN", "拥堵"] if "CAN" in text else ["界面"],
            "quality_flags": [],
            "content_hash": case_id,
            "generated_at": "",
        }
        embedding = {
            "document_id": document["document_id"],
            "case_id": case_id,
            "model": "local-hash-v1",
            "dimensions": 256,
            "vector": client.embed(text).vector,
            "content_hash": case_id,
            "generated_at": "",
        }
        document_path = docs_dir / f"{case_id}.json"
        embedding_path = embeddings_dir / f"{case_id}.json"
        document_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        embedding_path.write_text(json.dumps(embedding, ensure_ascii=False), encoding="utf-8")
        records.append({
            "document_id": document["document_id"],
            "case_id": case_id,
            "title": title,
            "organization": document["organization"],
            "classification": document["classification"],
            "filters": document["filters"],
            "tags": document["tags"],
            "quality_flags": [],
            "content_hash": case_id,
            "embedding_path": str(embedding_path.relative_to(root)),
            "retrieval_doc_path": str(document_path.relative_to(root)),
        })
    (index_dir / "case_index.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    return {"documents": len(records)}


if __name__ == "__main__":
    print(json.dumps(prepare(), ensure_ascii=False))
