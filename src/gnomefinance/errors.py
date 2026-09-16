class GNOMEfinanceError(Exception):
    """Base error for GNOMEfinance."""


class PriceAPIError(GNOMEfinanceError):
    """Raised when the price API cannot be reached."""


class InvalidCoinError(GNOMEfinanceError):
    """Raised when a coin is not available."""
