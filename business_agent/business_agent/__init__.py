"""BUSINESS_AGENT runtime package."""

from pathlib import Path

# Compatibility bridge:
# Historical contract/validator packages are stored at the project root
# (business_agent/contracts and business_agent/validators), while the runtime
# package lives in business_agent/business_agent. Extend the package search
# path so both layouts remain import-compatible.
_project_root = Path(__file__).resolve().parent.parent
_project_root_text = str(_project_root)
if _project_root_text not in __path__:
    __path__.append(_project_root_text)
