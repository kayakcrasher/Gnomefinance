class Transaction:
    def __init__(
        self,
        network,
        transaction_type,
        amount,
        asset
    ):
        self.network = network
        self.transaction_type = transaction_type
        self.amount = amount
        self.asset = asset

    def show(self):
        print(f"Network: {self.network}")
        print(f"Type: {self.transaction_type}")
        print(f"Amount: {self.amount}")
        print(f"Asset: {self.asset}")
