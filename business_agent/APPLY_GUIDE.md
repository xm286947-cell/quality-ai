# APPLY GUIDE

## 1. Correct target path

Copy the package files to:

`business_agent/business_agent/adapters/`

The previous upload created the wrong path:

`business_agent/adapters/`

Remove that incorrect directory after applying this package.

## 2. Apply API patch

From repository root:

```bash
git apply BUSINESS_AGENT_ENGINE_V1.2_M1_P02_Increment02_FIX/patches/api.py.patch
```

Or manually apply the changes shown in `patches/api.py.patch`.

## 3. Run tests

```bash
cd business_agent
pytest -q tests/test_m1_p02_contract_adapters.py
pytest -q
```

## 4. Important fix

`TraceContext` has `debug`, not `metadata`. This package fixes that incompatibility.
