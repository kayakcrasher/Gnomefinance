"""Manually entered holdings (coins on exchanges, cold storage, etc.)."""

from . import assets
from .errors import ValidationError


def parse_amount(value):
    """Turn user input into a non-negative float, or raise ValidationError."""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Not a number: {value!r}") from None

    if amount != amount or amount in (float("inf"), float("-inf")):
        raise ValidationError("Amount must be a finite number.")

    if amount < 0:
        raise ValidationError("Amount cannot be negative.")

    return amount


def check_asset(asset_id):
    if not assets.is_known(asset_id):
        raise ValidationError(f"Unknown asset: {asset_id}")


class Portfolio:
    def __init__(self, holdings=None):
        self._holdings = {}

        for asset_id, amount in (holdings or {}).items():
            self.set(asset_id, amount)

    def add(self, asset_id, amount):
        """Add to an existing holding (e.g. you bought more)."""
        check_asset(asset_id)
        amount = parse_amount(amount)
        self.set(asset_id, self.amount(asset_id) + amount)

    def set(self, asset_id, amount):
        """Set a holding to an exact amount. Zero removes it."""
        check_asset(asset_id)
        amount = parse_amount(amount)

        if amount == 0:
            self.remove(asset_id)
        else:
            self._holdings[asset_id] = amount

    def remove(self, asset_id):
        self._holdings.pop(asset_id, None)

    def clear(self):
        self._holdings.clear()

    def amount(self, asset_id):
        return self._holdings.get(asset_id, 0.0)

    @property
    def holdings(self):
        """A copy, so callers cannot change the portfolio by accident."""
        return dict(self._holdings)

    def __len__(self):
        return len(self._holdings)

    def __contains__(self, asset_id):
        return asset_id in self._holdings
