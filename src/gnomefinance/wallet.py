class Wallet:
    def __init__(self, address, network):
        self.address = address
        self.network = network

    def show(self):
        print(f"Network: {self.network}")
        print(f"Address: {self.address}")
