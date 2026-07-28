# Reuse Report — KC V1.1 Sprint-01 I03

| Existing asset | Strategy | Current use |
|---|---|---|
| ConfigLoader | Direct Reuse | Loads app/model/retrieval configuration inside JsonProviderAdapter |
| JsonArtifactRepository | Direct Reuse | JSON get/list access behind provider adapter |
| CaseRetriever | Direct Reuse | Search execution behind repository boundary |
| EmbeddingClient | Indirect Reuse | Used unchanged by CaseRetriever |
| Service Registry/Profile Loader | Reuse | Runtime service and configuration resolution |
| Compatibility entry | Reuse | Existing legacy-to-contract path retained |

No existing business retrieval implementation was deleted or rewritten.
