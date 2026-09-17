# network_interface.py


class NetworkInterface:
    """Base interface for blockchain networks."""

    def get_balance(self, address):
        """Return the balance for an address."""

        raise NotImplementedError(
            "Network must implement get_balance()."
        )

    def get_transaction(
        self,
        transaction_id,
    ):
        """Return transaction information."""

        raise NotImplementedError(
            "Network must implement "
            "get_transaction()."
        )

    def validate_address(self, address):
        """Validate a blockchain address."""

        raise NotImplementedError(
            "Network must implement "
            "validate_address()."
        )

    def get_network_name(self):
        """Return the network name."""

        raise NotImplementedError(
            "Network must implement "
            "get_network_name()."
        )

    def get_symbol(self):
        """Return the native asset symbol."""

        raise NotImplementedError(
            "Network must implement "
            "get_symbol()."
        )

    def is_connected(self):
        """Return whether the network is reachable."""

        raise NotImplementedError(
            "Network must implement "
            "is_connected()."
        )
