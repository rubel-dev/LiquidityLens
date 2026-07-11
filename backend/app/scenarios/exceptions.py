class ScenarioError(Exception):
    """Base error for deterministic scenario generation."""


class ScenarioNotFoundError(ScenarioError):
    pass


class ScenarioReplayError(ScenarioError):
    pass


class DuplicateScenarioRunError(ScenarioError):
    pass


class UnsafeSyntheticIdentifierError(ScenarioError):
    pass


class ScenarioResetError(ScenarioError):
    pass
