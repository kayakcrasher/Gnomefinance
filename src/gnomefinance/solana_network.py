import requests

from error_handler import APIError, NetworkError


class SolanaRPC:
    """Basic read-only Solana JSON-RPC client."""

    def __init__(
        self,
        rpc_url="https://api.mainnet-beta.solana.com",
        timeout=10,
    ):
        self.rpc_url = rpc_url
        self.timeout = timeout

    def call(self, method, params=None):
        """Send a JSON-RPC request to Solana."""

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }

        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()
            data = response.json()

        except requests.exceptions.Timeout as error:
            raise NetworkError(
                "Solana RPC request timed out."
            ) from error

        except requests.exceptions.ConnectionError as error:
            raise NetworkError(
                "Could not connect to Solana RPC."
            ) from error

        except requests.exceptions.HTTPError as error:
            raise APIError(
                f"Solana RPC HTTP error: {error}"
            ) from error

        except requests.exceptions.JSONDecodeError as error:
            raise APIError(
                "Solana RPC returned invalid JSON."
            ) from error

        except requests.exceptions.RequestException as error:
            raise APIError(
                f"Solana RPC request failed: {error}"
            ) from error

        if "error" in data:
            raise APIError(str(data["error"]))

        return data.get("result")

    def get_balance(self, address):
        """Return a Solana account balance in lamports."""

        result = self.call(
            "getBalance",
            [address],
        )

        if not result:
            return 0

        return result.get("value", 0)

    def get_balance_sol(self, address):
        """Return a Solana account balance in SOL."""

        lamports = self.get_balance(address)

        return lamports / 1_000_000_000

    def get_account_info(self, address):
        """Return information about a Solana account."""

        return self.call(
            "getAccountInfo",
            [
                address,
                {
                    "encoding": "jsonParsed",
                },
            ],
        )

    def get_transaction(self, transaction_id):
        """Return transaction information from Solana."""

        return self.call(
            "getTransaction",
            [
                transaction_id,
                {
                    "encoding": "jsonParsed",
                    "maxSupportedTransactionVersion": 0,
                },
            ],
        )

    def get_latest_blockhash(self):
        """Return the latest Solana blockhash."""

        result = self.call(
            "getLatestBlockhash"
        )

        if not result:
            return None

        return result.get("value", {})

    def get_slot(self):
        """Return the current Solana slot."""

        return self.call("getSlot")

    def is_connected(self):
        """Check whether the Solana RPC is reachable."""

        try:
            self.get_slot()
            return True

        except (APIError, NetworkError):
            return False


if __name__ == "__main__":
    rpc = SolanaRPC()

    print("GNOMEfinance Solana RPC")
    print("-----------------------")

    try:
        slot = rpc.get_slot()

        print("Current slot:", slot)
        print("RPC connected:", rpc.is_connected())

    except (APIError, NetworkError) as error:
        print("Solana RPC error:", error)
