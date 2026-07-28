# KNOWLEDGE_CAPABILITY_ENGINE V1.1 M1 I08

Status: Ready For Integration Test

## Purpose

补齐 M1 提测所需的 README、启动说明、配置说明、测试范围和可执行检查命令。

## Changes

- 更新根目录 README 至 V1.1 M1 I08
- 明确当前交付为 Python Runtime + CLI，不是常驻 HTTP 服务
- 增加 `docs/M1_I08_TEST_GUIDE.md`
- 增加 `run_i08_check.py`
- 增加 `tests/test_kc_runtime_i08.py`

## Test Commands

```bash
python kc_validate.py
python kc_query.py --text "软件运行过程中偶发崩溃" --top-k 5
python run_i08_check.py
python -m pytest -q
```
