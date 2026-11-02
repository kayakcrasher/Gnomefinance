"""A tiny time-limited (TTL) cache.

Public APIs rate-limit us, so we remember answers for a short while
instead of asking again on every page load.
"""

import time


class TTLCache:
    def __init__(self, ttl=60, clock=time.monotonic):
        self.ttl = ttl
        self.clock = clock
        self._items = {}

    def get(self, key, max_age=None):
        """Return a cached value, or None if missing or expired."""
        item = self._items.get(key)

        if item is None:
            return None

        value, saved_at = item
        limit = self.ttl if max_age is None else max_age

        if self.clock() - saved_at > limit:
            return None

        return value

    def get_stale(self, key):
        """Return the last value even if it expired (for offline fallback)."""
        item = self._items.get(key)
        return None if item is None else item[0]

    def set(self, key, value):
        self._items[key] = (value, self.clock())

    def age(self, key):
        item = self._items.get(key)
        return None if item is None else self.clock() - item[1]

    def has(self, key):
        return self.get(key) is not None

    def clear(self, key=None):
        if key is None:
            self._items.clear()
        else:
            self._items.pop(key, None)
