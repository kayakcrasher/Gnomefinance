# error_handler.py


class GNOMEFinanceError(Exception):
    """Base exception for GNOMEfinance."""

    pass


class APIError(GNOMEFinanceError):
    """Raised when an API request fails."""

    pass


class NetworkError(GNOMEFinanceError):
    """Raised when a network operation fails."""

    pass


class DataError(GNOMEFinanceError):
    """Raised when returned data is invalid."""

    pass


def handle_error(error):
    """Return a clean message for a GNOMEfinance error."""

    if isinstance(error, APIError):
        return f"API error: {error}"

    if isinstance(error, NetworkError):
        return f"Network error: {error}"

    if isinstance(error, DataError):
        return f"Data error: {error}"

    if isinstance(error, GNOMEFinanceError):
        return f"GNOMEfinance error: {error}"

    return f"Unexpected error: {error}"


def print_error(error):
    """Display a clean error message."""

    print(
        f"GNOMEfinance: "
        f"{handle_error(error)}"
    )


if __name__ == "__main__":

    try:
        raise APIError(
            "Market API is unavailable."
        )

    except GNOMEFinanceError as error:
        print_error(error)
