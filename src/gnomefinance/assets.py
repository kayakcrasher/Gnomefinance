class Asset:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    def show(self):
        print(f"{self.name} ({self.symbol})")
