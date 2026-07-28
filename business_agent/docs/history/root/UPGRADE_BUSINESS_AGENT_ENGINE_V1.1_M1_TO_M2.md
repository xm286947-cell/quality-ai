# Upgrade Guide: M1 → M2

1. Replace the complete project with the M2 package.
2. Preserve local `.env`, model configuration, knowledge data, input and output directories as needed.
3. Run `python main.py list-agents` and confirm `repeat_case` version is `2.4-m6-platform-m2`.
4. Run an existing REPEAT_CASE command for compatibility verification.
5. Run the unified runtime command for platform verification.

No data migration is required in this version.
