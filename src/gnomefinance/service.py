"""GNOMEfinance's brain: ties portfolio, wallets, prices and storage together.

The web app, desktop GUI and command line all talk to this one class, so
they always agree on the numbers.
"""

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from . import assets
from .cache import TTLCache
from .chains import default_chains
from .config import BALANCE_CACHE_TTL
from .errors import GNOMEfinanceError, ValidationError
from .market import MarketData
from .portfolio import Portfolio
from .storage import Storage

MAX_LABEL_LENGTH = 40


class GnomeFinance:
    def __init__(self, storage=None, market=None, chains=None):
        self.storage = storage or Storage()
        self.market = market or MarketData()
        self.chains = chains if chains is not None else default_chains()
        self.balance_cache = TTLCache(ttl=BALANCE_CACHE_TTL)
        self._lock = threading.Lock()

        saved = self.storage.load()
        self.portfolio = Portfolio()
        for asset_id, amount in saved["holdings"].items():
            if assets.is_known(asset_id):
                self.portfolio.set(asset_id, amount)
        self.wallets = [
            wallet for wallet in saved["wallets"]
            if wallet.get("chain") in self.chains
        ]

    # -- Manual holdings ---------------------------------------------------

    def set_holding(self, asset_id, amount):
        with self._lock:
            self.portfolio.set(asset_id, amount)
            self._save()

    def add_holding(self, asset_id, amount):
        with self._lock:
            self.portfolio.add(asset_id, amount)
            self._save()

    def remove_holding(self, asset_id):
        with self._lock:
            self.portfolio.remove(asset_id)
            self._save()

    def clear_holdings(self):
        with self._lock:
            self.portfolio.clear()
            self._save()

    # -- Tracked wallets ---------------------------------------------------

    def add_wallet(self, chain_id, address, label=""):
        chain = self.chains.get(chain_id)
        if chain is None:
            raise ValidationError(f"Unsupported chain: {chain_id}")

        address = chain.clean_address(address)
        label = (label or "").strip()[:MAX_LABEL_LENGTH]

        with self._lock:
            for wallet in self.wallets:
                if wallet["chain"] == chain_id and wallet["address"] == address:
                    raise ValidationError("You are already tracking that wallet.")

            wallet = {
                "id": uuid.uuid4().hex[:8],
                "chain": chain_id,
                "address": address,
                "label": label or f"{chain.name} wallet",
            }
            self.wallets.append(wallet)
            self._save()

        return wallet

    def remove_wallet(self, wallet_id):
        with self._lock:
            before = len(self.wallets)
            self.wallets = [w for w in self.wallets if w["id"] != wallet_id]
            if len(self.wallets) == before:
                raise ValidationError(f"No wallet with id {wallet_id}")
            self._save()

    def lookup_balance(self, chain_id, address):
        """Read any address's balance without saving it."""
        chain = self.chains.get(chain_id)
        if chain is None:
            raise ValidationError(f"Unsupported chain: {chain_id}")
        return chain.get_balance(address)

    def wallet_balances(self, force=False):
        """Fetch balances for every tracked wallet, in parallel.

        Returns a list of wallets with "balance" (or None) and "error".
        """
        def fetch(wallet):
            key = (wallet["chain"], wallet["address"])
            balance = None if force else self.balance_cache.get(key)
            error = None

            if balance is None:
                try:
                    balance = self.lookup_balance(*key)
                    self.balance_cache.set(key, balance)
                except GNOMEfinanceError as exc:
                    balance = self.balance_cache.get_stale(key)
                    error = str(exc)

            chain = self.chains[wallet["chain"]]
            return {
                **wallet,
                "asset_id": chain.asset_id,
                "symbol": assets.symbol(chain.asset_id),
                "balance": balance,
                "error": error,
                "explorer_url": chain.explorer_url(wallet["address"]),
            }

        wallets = list(self.wallets)
        if not wallets:
            return []

        with ThreadPoolExecutor(max_workers=min(8, len(wallets))) as pool:
            return list(pool.map(fetch, wallets))

    # -- Market data -------------------------------------------------------

    def quotes(self, force=False):
        return self.market.get_quotes(force=force)

    def history(self, asset_id, days=7):
        return self.market.get_history(asset_id, days)

    # -- The big picture ---------------------------------------------------

    def summary(self, force=False):
        """Everything a dashboard needs, with all the math done."""
        errors = []

        try:
            quotes = self.quotes(force=force)
        except GNOMEfinanceError as error:
            quotes = {}
            errors.append(f"Prices unavailable: {error}")

        wallets = self.wallet_balances(force=force)
        for wallet in wallets:
            if wallet["error"]:
                errors.append(f"{wallet['label']}: {wallet['error']}")

        on_chain = {}
        for wallet in wallets:
            if wallet["balance"] is not None:
                asset_id = wallet["asset_id"]
                on_chain[asset_id] = on_chain.get(asset_id, 0) + wallet["balance"]

        manual = self.portfolio.holdings
        rows = []

        for asset_id in assets.ASSETS:
            amount_manual = manual.get(asset_id, 0.0)
            amount_chain = on_chain.get(asset_id, 0.0)
            amount = amount_manual + amount_chain

            if amount <= 0 and asset_id not in manual:
                continue

            quote = quotes.get(asset_id)
            price = quote["price"] if quote else None
            change_pct = quote["change_24h"] if quote else 0.0
            value = amount * price if price is not None else None

            # Value 24h ago = value / (1 + change%), so the USD move is:
            if value is not None and change_pct > -100:
                value_change = value - value / (1 + change_pct / 100)
            else:
                value_change = 0.0

            info = assets.get_asset(asset_id)
            wallet_count = sum(1 for w in wallets if w["asset_id"] == asset_id)
            rows.append({
                "asset_id": asset_id,
                "name": info["name"],
                "symbol": info["symbol"],
                "icon": info["icon"],
                "amount": amount,
                "manual_amount": amount_manual,
                "wallet_amount": amount_chain,
                "wallet_count": wallet_count,
                "price": price,
                "change_24h": change_pct,
                "value": value,
                "value_change_24h": value_change,
            })

        total = sum(row["value"] or 0 for row in rows)
        total_change = sum(row["value_change_24h"] for row in rows)
        previous_total = total - total_change

        for row in rows:
            row["allocation"] = (
                (row["value"] or 0) / total * 100 if total > 0 else 0.0
            )

        rows.sort(key=lambda row: row["value"] or 0, reverse=True)

        return {
            "assets": rows,
            "wallets": wallets,
            "total_value": total,
            "change_24h": total_change,
            "change_24h_pct": (
                total_change / previous_total * 100 if previous_total > 0 else 0.0
            ),
            "prices_stale": any(q.get("stale") for q in quotes.values()),
            "errors": errors,
        }

    # -- Internals ---------------------------------------------------------

    def _save(self):
        self.storage.save(self.portfolio.holdings, self.wallets)
