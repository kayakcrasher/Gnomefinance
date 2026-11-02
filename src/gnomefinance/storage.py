"""Save and load the portfolio and tracked wallets as JSON."""

import json
import os
import tempfile
from pathlib import Path

from .config import PORTFOLIO_FILE
from .errors import GNOMEfinanceError


class Storage:
    def __init__(self, path=PORTFOLIO_FILE):
        self.path = Path(path)

    def load(self):
        """Return {"holdings": {...}, "wallets": [...]}."""
        if not self.path.exists():
            return {"holdings": {}, "wallets": []}

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise GNOMEfinanceError(
                f"Could not read {self.path}: {error}"
            ) from error

        # Older versions saved just {"bitcoin": 0.5, ...}.
        if "holdings" not in data and "wallets" not in data:
            return {"holdings": data, "wallets": []}

        return {
            "holdings": data.get("holdings", {}),
            "wallets": data.get("wallets", []),
        }

    def save(self, holdings, wallets):
        """Write atomically: a crash mid-save never corrupts the file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"holdings": holdings, "wallets": wallets}

        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            os.replace(tmp, self.path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
