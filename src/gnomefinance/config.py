# config.py

from pathlib import Path


APP_NAME = "GNOMEfinance"
APP_VERSION = "0.1.0"


# Storage
DATA_DIR = Path("data")
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"


# Market Data
API_URL = "https://api.coingecko.com/api/v3"
COINGECKO_BASE_URL = API_URL
CURRENCY = "usd"
API_TIMEOUT = 10
MARKET_CACHE_TTL = 60


# GUI
WINDOW_TITLE = APP_NAME
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 900


# Development
DEMO_MODE = False


def ensure_data_directory():
    """Create the application data directory."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_window_geometry():
    """Return the configured GUI dimensions."""
    return f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"


if __name__ == "__main__":
    print(f"{APP_NAME} v{APP_VERSION}")
    print("Data directory:", DATA_DIR)
    print("Portfolio file:", PORTFOLIO_FILE)
    print("Market cache TTL:", MARKET_CACHE_TTL)
    print("Window:", get_window_geometry())
    ensure_data_directory()
    print("Data directory ready.")
