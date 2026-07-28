# CHANGELOG - KNOWLEDGE_CAPABILITY_ENGINE V1.1

## M1 Iteration-02 - Existing Asset Integration

### Added

- `config/knowledge_services/registry.yaml`
- `knowledge_capability/runtime/service_catalog.py`
- `knowledge_capability/runtime/service_factory.py`
- `tests/test_kc_m1_i02_asset_integration.py`

### Changed

- `knowledge_capability/runtime/bootstrap.py`
  - Removed hard-coded Repeat Case registration.
  - Runtime is now assembled from the service catalog.
- `knowledge_capability/profiles/loader.py`
  - Added `service_type` and required-field validation.
- `knowledge_capability/framework/runtime.py`
  - Added explicit contract validation, service resolution and failure trace.
- `config/knowledge_services/repeat_case_service.yaml`
  - Added `service_type: repeat_case`.

### Reused Without Modification

- `retriever/case_retriever.py`
- `repositories/json_repository.py`
- `common/config_loader.py`
- Existing Repeat Case business pipeline

### Compatibility

- Legacy Repeat Case entry remains unchanged.
- Existing Repeat Case command chain remains unchanged.
- No existing business rule was moved into the platform.

## Sprint-01 / M1 I03 — Repository Boundary

### Added
- KnowledgeRepository protocol and RepositorySearchResult
- RepositoryFactory
- ProviderAdapter and JsonProviderAdapter
- KnowledgeSource model and KnowledgeSourceRegistry
- `config/knowledge_services/sources.yaml`
- Repository/provider/source trace details

### Changed
- RepeatCaseKnowledgeService now depends on KnowledgeRepository instead of constructing CaseRetriever directly
- ServiceFactory now assembles Profile + Source + Repository + Service
- Bootstrap passes resolved Service Profile into ServiceFactory

### Preserved
- CaseRetriever retrieval logic
- JsonArtifactRepository implementation
- Legacy Repeat Case execution path

## M1 I07 - Stabilization

- Added runtime configuration validation and `kc_validate.py`.
- Stabilized profile/config error mapping.
- Restored runtime public exports while preventing circular imports.
- Added compatibility and configuration regression coverage.
- Full project regression: 139 passed.
