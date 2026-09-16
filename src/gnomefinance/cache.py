import time


class PriceCache:
    def __init__(self, duration=30):
        self.duration = duration
        self.prices = {}

    def save(self, coin_id, price):
        self.prices[coin_id] = {
            "price": price,
            "time": time.time()
        }

    def get(self, coin_id):
        if coin_id not in self.prices:
            return None

        saved_data = self.prices[coin_id]

        age = time.time() - saved_data["time"]

        if age > self.duration:
            return None

        return saved_data["price"]

    def has(self, coin_id):
        return self.get(coin_id) is not None
