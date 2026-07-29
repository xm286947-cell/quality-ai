# APPLY GUIDE

## 应用方式

在现有 `business_agent` 工程根目录执行：

```bash
unzip BUSINESS_AGENT_ENGINE_V1.2_M3_P01_INCREMENT.zip -d /tmp/m3_p01
cp -R /tmp/m3_p01/BUSINESS_AGENT_ENGINE_V1.2_M3_P01_INCREMENT/business_agent/* business_agent/
cp -R /tmp/m3_p01/BUSINESS_AGENT_ENGINE_V1.2_M3_P01_INCREMENT/tests/* tests/
```

也可以直接将增量包中的同名文件覆盖到当前工程。

## 验证

```bash
pytest -q tests/test_m3_p01_contract_models.py
pytest -q
```

预期：

```text
5 passed
146 passed
```

## 新代码导入方式

```python
from business_agent.contracts import ExecutionRequest, KnowledgeRequestContract
from business_agent.validators import ContractValidator
```

原有导入仍然有效：

```python
from business_agent.api_contract import ExecutionResponse, ErrorResponse
```
