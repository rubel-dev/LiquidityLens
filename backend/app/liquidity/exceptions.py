class LiquidityForecastingError(Exception):
    """Base liquidity forecasting module error."""


class InvalidForecastInputError(LiquidityForecastingError):
    pass


class LiquidityPersistenceError(LiquidityForecastingError):
    pass


class ForecastSubjectNotFoundError(LiquidityForecastingError):
    pass
