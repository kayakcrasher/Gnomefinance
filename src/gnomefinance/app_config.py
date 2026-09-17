# app_config.py

from config import (
    APP_NAME,
    APP_VERSION,
    API_TIMEOUT,
    COINGECKO_BASE_URL,
    MARKET_CACHE_TTL,
    PORTFOLIO_FILE,
    get_window_geometry,
)


class AppConfig:
    """Central configuration interface for GNOMEfinance."""

    def __init__(self):
        self.name = APP_NAME
        self.version = APP_VERSION

        self.api_timeout = API_TIMEOUT
        self.coingecko_base_url = (
            COINGECKO_BASE_URL
        )

        self.market_cache_ttl = (
            MARKET_CACHE_TTL
        )

        self.portfolio_file = (
            PORTFOLIO_FILE
        )

        self.window_geometry = (
            get_window_geometry()
        )

    def display(self):
        """Display application configuration."""

        print("GNOMEfinance Configuration")
        print("--------------------------")

        print(
            f"Application: "
            f"{self.name}"
        )

        print(
            f"Version: "
            f"{self.version}"
        )

        print(
            f"API timeout: "
            f"{self.api_timeout}s"
        )

        print(
            f"Market cache: "
            f"{self.market_cache_ttl}s"
        )

        print(
            f"Portfolio file: "
            f"{self.portfolio_file}"
        )

        print(
            f"Window: "
            f"{self.window_geometry}"
        )


if __name__ == "__main__":

    config = AppConfig()

    config.display()
