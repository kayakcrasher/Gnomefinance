# market_cache.py

import time


class MarketCache:
    """Temporary in-memory cache for market data."""

    def __init__(self, ttl=60):
        """
        Create a market cache.

        ttl:
            Number of seconds before cached data expires.
        """

        self.ttl = ttl
        self.data = None
        self.timestamp = 0

    def is_valid(self):
        """Return True if cached data is still fresh."""

        if self.data is None:
            return False

        age = time.time() - self.timestamp

        return age < self.ttl

    def get(self):
        """Return cached data if it is still valid."""

        if not self.is_valid():
            return None

        return self.data

    def set(self, data):
        """Store new data in the cache."""

        self.data = data
        self.timestamp = time.time()

    def clear(self):
        """Clear the cached data."""

        self.data = None
        self.timestamp = 0

    def age(self):
        """Return the age of the cached data."""

        if self.data is None:
            return None

        return time.time() - self.timestamp


if __name__ == "__main__":

    cache = MarketCache(
        ttl=60
    )

    print(
        "Cache valid:",
        cache.is_valid()
    )

    cache.set(
        {
            "bitcoin": {
                "price": 100000
            }
        }
    )

    print(
        "Cached data:",
        cache.get()
    )

    print(
        "Cache age:",
        f"{cache.age():.2f} seconds"
    )
