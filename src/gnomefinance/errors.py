"""Errors used across GNOMEfinance.

Everything inherits from GNOMEfinanceError, so callers can catch one type.
"""


class GNOMEfinanceError(Exception):
    """Base error for GNOMEfinance."""


class NetworkError(GNOMEfinanceError):
    """A remote service could not be reached (timeout, no connection)."""


class APIError(GNOMEfinanceError):
    """A remote service answered, but with an error or bad data."""


class ValidationError(GNOMEfinanceError, ValueError):
    """The user gave us something we cannot accept."""
