# DESIGN_CHANGE_CANDIDATES

Design remains V1.1 Frozen. The following entries are governance candidates only.

## Candidate-001 Repository Architecture

- Category: Architecture
- Source Project: KNOWLEDGE_CAPABILITY_ENGINE
- Source Milestone: M1
- Source Iteration: Sprint-01 I03
- Current Status: Pending
- Problem: Provider Adapter alone does not define the stable access boundary used by services and future management/retrieval capabilities.
- Current Engine Solution: Introduced `KnowledgeRepository` between service/retrieval callers and provider adapters.
- Commonality Analysis: Potential platform common capability; currently evidenced by the first migrated service only.
- Impact Scope: Knowledge Management, Knowledge Retrieval, Provider integration.
- Recommendation: Evaluate adding Repository Architecture after additional service evidence.
- Suggested Version: Design VNext, subject to Architecture Review.

## Candidate-002 Repository Factory

- Category: Runtime
- Source Project: KNOWLEDGE_CAPABILITY_ENGINE
- Source Milestone: M1
- Source Iteration: Sprint-01 I03
- Current Status: Pending
- Problem: Runtime needs a common assembly point from Profile and Source to provider-specific repository.
- Current Engine Solution: Added `RepositoryFactory`.
- Commonality Analysis: One-service evidence only.
- Impact Scope: Runtime assembly and provider replacement.
- Recommendation: Keep as candidate until another service/provider reuses it.
- Suggested Version: Design VNext, subject to Architecture Review.

## Candidate-003 Repository Contract

- Category: Contract
- Source Project: KNOWLEDGE_CAPABILITY_ENGINE
- Source Milestone: M1
- Source Iteration: Sprint-01 I03
- Current Status: Pending
- Problem: Services require stable `search/get/list/metadata` access without depending on provider implementation.
- Current Engine Solution: Added the `KnowledgeRepository` protocol and `RepositorySearchResult`.
- Commonality Analysis: Stable in current engine but not yet validated across multiple services.
- Impact Scope: Service Framework, Management, Retrieval.
- Recommendation: Validate through M2 and a second Knowledge Service before acceptance.
- Suggested Version: Design VNext, subject to Architecture Review.
