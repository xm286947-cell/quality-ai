# Knowledge Capability Runtime

## 运行查询

```bash
python kc_query.py --service-id repeat_case_service --text "待检索的问题描述" --top-k 5
```

CLI 只构造 `KnowledgeRequest`，服务、Profile、Repository 与 Provider 由 Runtime 自动装配。

## 启动前配置校验

```bash
python kc_validate.py
```

校验内容包括：服务目录可读取、Profile 可读取、service_id 一致、服务状态合法、服务无重复注册。

## 兼容入口

`KnowledgeCapabilityRuntime.query(request)` 保留为 `execute(request)` 的兼容入口。
