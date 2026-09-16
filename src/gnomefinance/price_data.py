class Price:
    def __init__(self, coin_id, symbol, usd):
        self.coin_id = coin_id
        self.symbol = symbol
        self.usd = usd

    def show(self):
        if self.usd is None:
            print(f"{self.symbol}: Price unavailable")
        else:
            print(f"{self.symbol}: ${self.usd:,.2f}")
