from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "business_agent.api.app:app",
        host=os.getenv("BUSINESS_AGENT_HTTP_HOST", "127.0.0.1"),
        port=int(os.getenv("BUSINESS_AGENT_HTTP_PORT", "8090")),
        reload=False,
    )


if __name__ == "__main__":
    main()
