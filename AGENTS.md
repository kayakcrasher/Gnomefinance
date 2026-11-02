# GNOMEfinance Instructions

## Project

GNOMEfinance is being built one piece at a time.

## Development Rules

- Keep the code simple.
- Build one feature at a time.
- Test every new piece.
- Don't rewrite working code without a reason.
- Explain new concepts while building.
- Keep secrets and API keys out of the repository.

## Current Focus

Learn Python by building GNOMEfinance.

## Structure

- All app logic goes through `service.py` (`GnomeFinance`); the web app, GUI and CLI only display it.
- Use package-relative imports (`from .market import MarketData`).
- Tests live in `tests/` and must never call the real internet; use the fakes in `tests/conftest.py`.
- Run `pytest` before committing.

## Important

When adding a new feature, make the smallest useful version first.

Then improve it.
