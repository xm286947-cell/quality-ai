class KnowledgeError(RuntimeError):
    """Base error for Knowledge Capability integration."""


class KnowledgeConfigurationError(KnowledgeError):
    pass


class KnowledgeTransportError(KnowledgeError):
    pass


class KnowledgeContractError(KnowledgeError):
    pass
