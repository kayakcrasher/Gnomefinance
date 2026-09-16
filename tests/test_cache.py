from src.gnomefinance.cache import PriceCache


cache = PriceCache(duration=30)

print("Cache has Bitcoin:", cache.has("bitcoin"))

cache.save("bitcoin", 65000)

print("Cache has Bitcoin:", cache.has("bitcoin"))

price = cache.get("bitcoin")

print(f"Cached Bitcoin price: ${price:,.2f}")
