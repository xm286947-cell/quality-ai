from __future__ import annotations

from typing import Any

from .binding import CapabilityBinding
from .errors import CapabilityNotFoundError, CapabilityValidationError


class ServiceLocator:
    """Resolves Agent Profile capability bindings without leaking provider details."""

    def load_profile_bindings(self, profile: Any) -> dict[tuple[str, str], CapabilityBinding]:
        raw_bindings = getattr(profile, "capability_bindings", None)
        if raw_bindings is None:
            raw_bindings = self._metadata_bindings(profile)
        return self.parse_bindings(raw_bindings or {})

    def parse_bindings(
        self,
        raw_bindings: dict[str, Any],
    ) -> dict[tuple[str, str], CapabilityBinding]:
        if not isinstance(raw_bindings, dict):
            raise CapabilityValidationError("capability_bindings must be a mapping")
        parsed: dict[tuple[str, str], CapabilityBinding] = {}
        for capability_type, bindings in raw_bindings.items():
            if not isinstance(bindings, dict):
                raise CapabilityValidationError(
                    f"capability group '{capability_type}' must be a mapping"
                )
            for binding_name, raw in bindings.items():
                if not isinstance(raw, dict):
                    raise CapabilityValidationError(
                        f"binding '{capability_type}.{binding_name}' must be a mapping"
                    )
                binding = CapabilityBinding.from_dict(
                    str(binding_name), str(capability_type), raw
                )
                parsed[(binding.capability_type, binding.binding_name)] = binding
        return parsed

    def resolve(
        self,
        bindings: dict[tuple[str, str], CapabilityBinding],
        capability_type: str,
        binding_name: str,
    ) -> CapabilityBinding:
        key = (capability_type, binding_name)
        try:
            return bindings[key]
        except KeyError as exc:
            raise CapabilityNotFoundError(
                f"capability binding not found: {capability_type}.{binding_name}"
            ) from exc

    @staticmethod
    def _metadata_bindings(profile: Any) -> dict[str, Any]:
        metadata = getattr(profile, "metadata", {}) or {}
        return dict(metadata.get("capability_bindings") or {})
