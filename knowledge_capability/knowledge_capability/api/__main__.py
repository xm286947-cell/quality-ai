from __future__ import annotations

import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "knowledge_capability.api.app:app",
        host=os.getenv("KC_HOST", "0.0.0.0"),
        port=int(os.getenv("KC_PORT", "8080")),
        reload=False,
    )
