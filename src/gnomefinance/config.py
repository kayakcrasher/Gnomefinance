"""Application settings.

Every setting can be overridden with an environment variable, so you never
have to edit code (or commit secrets) to change how the app behaves.
"""

import os
from pathlib import Path

APP_NAME = "GNOMEfinance"

# Project root: .../GNOMEfinance (two folders above this file's package).
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Storage
DATA_DIR = Path(os.environ.get("GNOMEFINANCE_DATA_DIR", PROJECT_ROOT / "data"))
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"

# Market data (CoinGecko)
COINGECKO_URL = "https://api.coingecko.com/api/v3"
# Optional free "demo" key from coingecko.com. Raises the rate limit.
COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")
CURRENCY = "usd"
API_TIMEOUT = float(os.environ.get("GNOMEFINANCE_API_TIMEOUT", 10))
MARKET_CACHE_TTL = int(os.environ.get("GNOMEFINANCE_CACHE_TTL", 60))
BALANCE_CACHE_TTL = 120

# Blockchain endpoints (all public, read-only)
SOLANA_RPC_URL = os.environ.get(
    "GNOMEFINANCE_SOLANA_RPC", "https://api.mainnet-beta.solana.com"
)
ETHEREUM_RPC_URL = os.environ.get(
    "GNOMEFINANCE_ETHEREUM_RPC", "https://ethereum-rpc.publicnode.com"
)
BITCOIN_API_URL = os.environ.get(
    "GNOMEFINANCE_BITCOIN_API", "https://mempool.space/api"
)

# Web server
WEB_HOST = os.environ.get("HOST", "127.0.0.1")
WEB_PORT = int(os.environ.get("PORT", 5000))
