"""Read-only wallet balance lookups for real blockchains.

GNOMEfinance never needs private keys: a public address is enough to read
a balance. Each chain class knows how to validate its addresses and ask a
public API for the balance.
"""

import hashlib
import re

from .api_client import APIClient
from .config import BITCOIN_API_URL, ETHEREUM_RPC_URL, SOLANA_RPC_URL
from .errors import APIError, ValidationError

# ---------------------------------------------------------------------------
# Address encodings
# ---------------------------------------------------------------------------

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58_decode(text):
    """Decode a Base58 string (used by Solana and old Bitcoin addresses)."""
    number = 0
    for char in text:
        index = BASE58_ALPHABET.find(char)
        if index < 0:
            raise ValueError(f"Invalid Base58 character: {char!r}")
        number = number * 58 + index

    body = number.to_bytes((number.bit_length() + 7) // 8, "big")
    leading_zeros = len(text) - len(text.lstrip("1"))
    return b"\x00" * leading_zeros + body


BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32_CONST = 1
BECH32M_CONST = 0x2BC830A3


def _bech32_polymod(values):
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    checksum = 1
    for value in values:
        top = checksum >> 25
        checksum = (checksum & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            if (top >> i) & 1:
                checksum ^= generator[i]
    return checksum


def _bech32_hrp_expand(hrp):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def is_valid_bech32_address(address, hrp="bc"):
    """Check a SegWit (bc1q...) or Taproot (bc1p...) address checksum."""
    if address.lower() != address and address.upper() != address:
        return False

    address = address.lower()
    if not 14 <= len(address) <= 90:
        return False

    separator = address.rfind("1")
    if address[:separator] != hrp or separator + 7 > len(address):
        return False

    try:
        data = [BECH32_CHARSET.index(c) for c in address[separator + 1:]]
    except ValueError:
        return False

    constant = _bech32_polymod(_bech32_hrp_expand(hrp) + data)
    witness_version = data[0]

    if witness_version == 0:
        return constant == BECH32_CONST
    return witness_version <= 16 and constant == BECH32M_CONST


def is_valid_base58check_address(address, versions=(0x00, 0x05)):
    """Check a legacy (1...) or script (3...) Bitcoin address checksum."""
    try:
        raw = base58_decode(address)
    except ValueError:
        return False

    if len(raw) != 25 or raw[0] not in versions:
        return False

    payload, checksum = raw[:-4], raw[-4:]
    digest = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
    return digest[:4] == checksum


# ---------------------------------------------------------------------------
# Chains
# ---------------------------------------------------------------------------


class Chain:
    id = ""
    name = ""
    asset_id = ""
    explorer = ""

    def validate_address(self, address):
        raise NotImplementedError

    def get_balance(self, address):
        """Return the balance in whole coins (BTC, ETH, SOL)."""
        raise NotImplementedError

    def clean_address(self, address):
        address = (address or "").strip()
        if not self.validate_address(address):
            raise ValidationError(f"That is not a valid {self.name} address.")
        return address

    def explorer_url(self, address):
        return self.explorer.format(address=address)


class BitcoinChain(Chain):
    id = "bitcoin"
    name = "Bitcoin"
    asset_id = "bitcoin"
    explorer = "https://mempool.space/address/{address}"

    def __init__(self, client=None):
        self.client = client or APIClient(BITCOIN_API_URL)

    def validate_address(self, address):
        if not isinstance(address, str):
            return False
        if address.lower().startswith("bc1"):
            return is_valid_bech32_address(address)
        return is_valid_base58check_address(address)

    def get_balance(self, address):
        address = self.clean_address(address)
        data = self.client.get(f"/address/{address}")

        try:
            confirmed = data["chain_stats"]
            pending = data["mempool_stats"]
            sats = (
                confirmed["funded_txo_sum"] - confirmed["spent_txo_sum"]
                + pending["funded_txo_sum"] - pending["spent_txo_sum"]
            )
        except (KeyError, TypeError) as error:
            raise APIError("Unexpected response from Bitcoin API.") from error

        return sats / 100_000_000


class EthereumChain(Chain):
    id = "ethereum"
    name = "Ethereum"
    asset_id = "ethereum"
    explorer = "https://etherscan.io/address/{address}"

    ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")

    def __init__(self, client=None):
        self.client = client or APIClient(ETHEREUM_RPC_URL)

    def validate_address(self, address):
        return isinstance(address, str) and bool(self.ADDRESS.match(address))

    def get_balance(self, address):
        address = self.clean_address(address)
        result = self.client.rpc("eth_getBalance", [address, "latest"])

        try:
            wei = int(result, 16)
        except (TypeError, ValueError) as error:
            raise APIError("Unexpected response from Ethereum RPC.") from error

        return wei / 10**18


class SolanaChain(Chain):
    id = "solana"
    name = "Solana"
    asset_id = "solana"
    explorer = "https://solscan.io/account/{address}"

    def __init__(self, client=None):
        self.client = client or APIClient(SOLANA_RPC_URL)

    def validate_address(self, address):
        if not isinstance(address, str) or not 32 <= len(address) <= 44:
            return False
        try:
            return len(base58_decode(address)) == 32
        except ValueError:
            return False

    def get_balance(self, address):
        address = self.clean_address(address)
        result = self.client.rpc("getBalance", [address])

        try:
            lamports = result["value"]
        except (KeyError, TypeError) as error:
            raise APIError("Unexpected response from Solana RPC.") from error

        return lamports / 1_000_000_000


def default_chains():
    return {
        chain.id: chain
        for chain in (BitcoinChain(), EthereumChain(), SolanaChain())
    }
