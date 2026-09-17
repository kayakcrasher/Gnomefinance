from .networks import NETWORKS


class Blockchain:
    def __init__(self, network):
        if network not in NETWORKS:
            raise ValueError(
                f"Unknown network: {network}"
            )

        self.network = network
        self.name = NETWORKS[network]["name"]
        self.type = NETWORKS[network]["type"]

    def show(self):
        print(f"Blockchain: {self.name}")
        print(f"Type: {self.type}")
