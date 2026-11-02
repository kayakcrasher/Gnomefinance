from gnomefinance.cache import TTLCache


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_get_returns_fresh_value():
    cache = TTLCache(ttl=30, clock=Clock())
    cache.set("bitcoin", 65000)
    assert cache.get("bitcoin") == 65000
    assert cache.has("bitcoin")


def test_value_expires_but_stale_copy_is_kept():
    clock = Clock()
    cache = TTLCache(ttl=30, clock=clock)
    cache.set("bitcoin", 65000)
    clock.now = 31
    assert cache.get("bitcoin") is None
    assert cache.get_stale("bitcoin") == 65000
    assert cache.age("bitcoin") == 31


def test_max_age_override_and_clear():
    clock = Clock()
    cache = TTLCache(ttl=30, clock=clock)
    cache.set("a", 1)
    clock.now = 50
    assert cache.get("a", max_age=60) == 1
    cache.clear()
    assert cache.get_stale("a") is None
