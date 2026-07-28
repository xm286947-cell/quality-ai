# M1 I08 集成测试指南

## 1. 提测包

```text
KNOWLEDGE_CAPABILITY_ENGINE_V1.1_M1_I08.zip
```

## 2. 测试准备

```bash
python -m pip install -r requirements.txt
python kc_validate.py
```

配置校验必须返回 `valid: true`。

## 3. 冒烟测试

### TC-01 Runtime 配置校验

```bash
python kc_validate.py
```

预期：退出码为 0，服务列表包含 `repeat_case_service`。

### TC-02 最小查询

```bash
python kc_query.py --text "软件运行过程中偶发崩溃" --top-k 5
```

预期：输出合法 JSON；`service_id` 为 `repeat_case_service`；错误不得以裸异常栈形式返回。

### TC-03 带过滤条件查询

```bash
python kc_query.py --text "通信报文过多导致处理拥堵" --product "DCDC" --domain "通信" --top-k 5
```

预期：请求成功进入 Runtime；过滤条件被传入服务；结果为空也不得导致 Runtime 异常。

### TC-04 Runtime Trace

检查查询结果中的 Trace，至少包含：

```text
contract_validation
service_resolution
profile_resolution
service_execute
result_mapping
```

### TC-05 错误映射

```bash
python kc_query.py --service-id missing_service --text "test"
```

预期：退出码非 0；返回统一错误对象；错误码为 `SERVICE_NOT_FOUND`，不抛出未处理异常。

## 4. 自动化测试

专项测试：

```bash
python -m pytest -q tests/test_kc_runtime_i06.py tests/test_kc_runtime_i07.py tests/test_kc_runtime_i08.py
```

全工程回归：

```bash
python -m pytest -q
```

一键检查：

```bash
python run_i08_check.py
```

## 5. 判定标准

以下全部满足才能判定 M1 集成测试通过：

- 配置校验通过
- Runtime 查询入口可执行
- Trace 完整
- 错误统一封装
- Repeat Case 服务可被 Registry 解析
- 专项测试全部通过
- 全工程回归无新增失败

## 6. 不在本次范围

- 常驻 Web 服务
- HTTP API
- Lifecycle、Metadata、Version、Schema Management
- Hybrid Retrieval、Ranking、Cache、Retry、Metrics
