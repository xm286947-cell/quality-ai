# CHANGELOG

## BUSINESS_AGENT_ENGINE V1.2 — M3-P01 Contract Model Refresh

### Added

- 新增统一公共 Contract 包 `business_agent.contracts`。
- 新增 Execution Request / Result Contract。
- 新增 Knowledge Request / Response / Item Contract。
- 新增 Evidence、Trace、Timing、Cost、Warning、Error、Metadata 公共模型。
- 新增 Contract Version 常量与支持版本集合。
- 新增 `ContractValidator`，支持版本校验和 Pydantic Schema 校验。
- 新增 P01 合同模型单元测试、序列化测试和兼容性测试。

### Changed

- `business_agent.api_contract` 改为向后兼容的重新导出层，现有调用方无需修改即可继续使用。

### Compatibility

- 保留原有 `business_agent.api_contract` 导入路径。
- 未修改现有 Runtime、Workflow、Knowledge Adapter 的执行逻辑。
- 现有 REPEAT_CASE HTTP Contract 回归测试保持通过。
