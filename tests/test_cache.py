from src.gnomefinance.cache import PriceCache


cache = PriceCache(duration=30)

cache.save("bitcoin", 65000)

price = cache.get("bitcoin")

print(f"Cached Bitcoin price: ${price:,.2f}")
