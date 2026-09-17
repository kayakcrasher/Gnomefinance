from gnomefinance.cache import PriceCache


def test_cache_save_and_get():
    cache = PriceCache(duration=30)

    cache.save("bitcoin", 65000)

    assert cache.has("bitcoin")
    assert cache.get("bitcoin") == 65000
