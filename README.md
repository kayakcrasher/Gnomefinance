# 🍄 GNOMEfinance

A personal crypto portfolio tracker with live prices, real on-chain wallet balances, and price charts. It's built one small piece at a time.

## What it does

- **Live market data**: BTC, ETH, SOL, ADA and AVAX prices with 24h change, from CoinGecko.
- **Price charts**: 1D / 7D / 1M / 3M / 1Y history for any coin.
- **Holdings**: enter coins you hold on exchanges or anywhere else, and see value, 24h gain/loss and allocation.
- **Wallet tracking**: paste a public **Bitcoin, Ethereum or Solana** address and its balance is read live from the blockchain. Addresses are checksum-validated. No private keys are ever needed or stored.
- **Solana dapp** (in the web dashboard): connect Phantom, Solflare or Backpack to
  - see every token in your wallet, with USD values,
  - **send** SOL or any SPL token (it creates the recipient's token account if needed), and
  - **swap** any token through Jupiter, with price impact and slippage shown up front.

  You approve every transaction in your own wallet, and the app never sees your keys. Switch to **Devnet** to practice with free test SOL.
- **Three ways to use it**: a web dashboard, a desktop app and a command line, all sharing the same data.
- **Works offline-ish**: if the price API is down, it shows the last known prices and tells you so.

Your portfolio is saved to `data/portfolio.json` on your own machine (git-ignored).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run it

**Web dashboard** (recommended):

```bash
python web_run.py
# open http://127.0.0.1:5000
```

**Desktop app** (needs tkinter, which is included with most Python installs):

```bash
python run.py
```

**Command line**:

```bash
cd src
python -m gnomefinance prices
python -m gnomefinance set BTC 0.25          # set a holding
python -m gnomefinance add SOL 3             # add to a holding
python -m gnomefinance wallet add solana <address> --label "Phantom"
python -m gnomefinance wallet list
python -m gnomefinance balance bitcoin <address>   # one-off lookup, not saved
python -m gnomefinance portfolio
```

(Or `pip install -e .` once, and then just use `gnomefinance prices` from anywhere.)

## GitHub Pages version

There's also a static version of the dashboard that needs no server. It's built by `scripts/build_static.py` and deployed by `.github/workflows/pages.yml` on every push to `main`. In that version:

- prices and wallet balances are fetched directly from the browser, and
- holdings are saved in the visitor's own browser (`localStorage`), so everyone who opens the page sees only their own data.

To try the static build locally:

```bash
python scripts/build_static.py
python -m http.server -d site 8000
```

## How the dapp works

`static/dapp.js` runs entirely in your browser:

1. **Connect:** asks your wallet extension for your public address (`provider.connect()`).
2. **Read:** token balances come from Jupiter's holdings API (mainnet) or straight from a Solana RPC node (devnet). Names and prices come from Jupiter's token API.
3. **Send:** builds the transaction instructions by hand, so you can read exactly what gets signed:
   - a small priority fee (compute budget),
   - a System Program transfer for SOL, or
   - "create the recipient's token account if missing" plus a `TransferChecked` for tokens.
4. **Swap:** gets a quote from Jupiter, then asks Jupiter to build the swap transaction. Before your wallet sees it, the app checks that you are the only signer and fee payer.
5. **Sign and confirm:** your wallet signs, the app sends the transaction through the RPC, and then waits until the network confirms it.

Safety rails:
- every transaction is shown in a confirm dialog before your wallet opens,
- sends to token accounts are refused (funds sent there are usually lost),
- 0.002 SOL is always kept back for fees,
- unverified tokens and high price impact are flagged, and swaps above 20% price impact are blocked.

Mainnet transactions use real money. Try things on Devnet first.

## Configuration

Everything is optional and set through environment variables, so no secrets ever go in the code.

| Variable | Default | What it does |
| --- | --- | --- |
| `COINGECKO_API_KEY` | none | Free CoinGecko demo key for higher rate limits |
| `GNOMEFINANCE_DATA_DIR` | `./data` | Where your portfolio is saved |
| `GNOMEFINANCE_SOLANA_RPC` | Solana public RPC | Use your own Solana RPC (e.g. Helius) |
| `GNOMEFINANCE_ETHEREUM_RPC` | publicnode.com | Use your own Ethereum RPC |
| `GNOMEFINANCE_BITCOIN_API` | mempool.space | Bitcoin address API |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Web server address |

> The web dashboard has no login. Keep it on `127.0.0.1` unless you add authentication.

## Project layout

```
src/gnomefinance/
  assets.py      the list of supported coins (add a coin here)
  market.py      prices + history from CoinGecko, with caching
  chains.py      Bitcoin / Ethereum / Solana address validation + balances
  portfolio.py   manually entered holdings
  storage.py     saving to JSON
  service.py     ties it all together; every interface uses this
  web_app.py     Flask JSON API + templates/ + static/
  gui.py         tkinter desktop app
  cli.py         command line
tests/           pytest suite (fully offline, uses fake API clients)
```

## Tests

```bash
pytest
```

## Roadmap

- [x] Python foundation
- [x] Cryptocurrency prices
- [x] Portfolio tracking
- [x] User interface (web, desktop, CLI)
- [x] Bitcoin tools (address validation, balances)
- [x] Solana tools (balances)
- [x] Solana dapp: wallet connect, SPL token balances, send, Jupiter swaps
- [ ] ERC-20 token balances
- [ ] Cost basis and profit/loss
- [ ] Portfolio value history over time
