class AnomalyDetectionError(Exception):
    """Base anomaly detection module error."""


class InvalidAnomalyInputError(AnomalyDetectionError):
    pass


class AnomalySubjectNotFoundError(AnomalyDetectionError):
    pass
