# 🍄 GNOMEfinance

A personal crypto portfolio tracker with live prices, real on-chain wallet balances, and price charts. It's built one small piece at a time.

## What it does

- **Live market data**: BTC, ETH, SOL, ADA and AVAX prices with 24h change, from CoinGecko.
- **Price charts**: 1D / 7D / 1M / 3M / 1Y history for any coin.
- **Holdings**: enter coins you hold on exchanges or anywhere else, and see value, 24h gain/loss and allocation.
- **Wallet tracking**: paste a public **Bitcoin, Ethereum or Solana** address and its balance is read live from the blockchain. Addresses are checksum-validated. No private keys are ever needed or stored.
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
- [ ] SPL / ERC-20 token balances
- [ ] Cost basis and profit/loss
- [ ] Portfolio value history over time
