"""Command line interface.

Examples:
    python -m gnomefinance prices
    python -m gnomefinance set BTC 0.25
    python -m gnomefinance wallet add solana <address> --label "Phantom"
    python -m gnomefinance portfolio
    python -m gnomefinance web
"""

import argparse
import sys

from . import __version__, assets
from .errors import GNOMEfinanceError


def money(value):
    if value is None:
        return "—"
    return f"${value:,.2f}" if abs(value) >= 1 else f"${value:,.6f}"


def signed_pct(value):
    return f"{value:+.2f}%"


def asset_arg(text):
    asset_id = assets.find_by_symbol(text)
    if asset_id is None:
        known = ", ".join(info["symbol"] for info in assets.ASSETS.values())
        raise argparse.ArgumentTypeError(f"unknown asset {text!r} (try: {known})")
    return asset_id


def cmd_prices(gf, args):
    quotes = gf.quotes(force=True)
    print(f"{'Asset':<12}{'Price':>16}{'24h':>10}")
    for asset_id, info in assets.ASSETS.items():
        quote = quotes.get(asset_id)
        if quote is None:
            print(f"{info['symbol']:<12}{'unavailable':>16}")
            continue
        print(
            f"{info['symbol']:<12}{money(quote['price']):>16}"
            f"{signed_pct(quote['change_24h']):>10}"
        )


def cmd_portfolio(gf, args):
    summary = gf.summary(force=True)

    if not summary["assets"]:
        print("Your portfolio is empty. Try: python -m gnomefinance set BTC 0.1")
        return

    print(f"{'Asset':<8}{'Amount':>18}{'Price':>15}{'Value':>20}{'24h':>9}{'Share':>8}")
    for row in summary["assets"]:
        print(
            f"{row['symbol']:<8}{row['amount']:>18,.8g}{money(row['price']):>15}"
            f"{money(row['value']):>20}{signed_pct(row['change_24h']):>9}"
            f"{row['allocation']:>7.1f}%"
        )

    print("-" * 78)
    print(
        f"{'TOTAL':<8}{money(summary['total_value']):>53}"
        f"   {'+' if summary['change_24h'] >= 0 else '-'}"
        f"{money(abs(summary['change_24h']))} ({signed_pct(summary['change_24h_pct'])}) today"
    )

    for error in summary["errors"]:
        print(f"warning: {error}", file=sys.stderr)


def cmd_set(gf, args):
    gf.set_holding(args.asset, args.amount)
    print(f"{assets.symbol(args.asset)} set to {gf.portfolio.amount(args.asset):g}")


def cmd_add(gf, args):
    gf.add_holding(args.asset, args.amount)
    print(f"{assets.symbol(args.asset)} is now {gf.portfolio.amount(args.asset):g}")


def cmd_remove(gf, args):
    gf.remove_holding(args.asset)
    print(f"Removed {assets.symbol(args.asset)}")


def cmd_wallet(gf, args):
    if args.action == "list":
        wallets = gf.wallet_balances(force=True)
        if not wallets:
            print("No wallets tracked.")
        for w in wallets:
            balance = "unavailable" if w["balance"] is None else f"{w['balance']:,.8g} {w['symbol']}"
            print(f"[{w['id']}] {w['label']:<20} {balance:>22}  {w['address']}")
            if w["error"]:
                print(f"         error: {w['error']}")
    elif args.action == "add":
        wallet = gf.add_wallet(args.chain, args.address, args.label)
        balance = gf.lookup_balance(wallet["chain"], wallet["address"])
        print(f"Tracking {wallet['label']} [{wallet['id']}]: {balance:,.8g}")
    elif args.action == "remove":
        gf.remove_wallet(args.wallet_id)
        print("Wallet removed.")


def cmd_balance(gf, args):
    balance = gf.lookup_balance(args.chain, args.address)
    print(f"{balance:,.9g}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="gnomefinance", description="Your crypto command center."
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("prices", help="show live prices")
    sub.add_parser("portfolio", help="show your portfolio value")

    for name, helptext in (("set", "set a holding to an exact amount"),
                           ("add", "add to a holding")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("asset", type=asset_arg)
        p.add_argument("amount")

    p = sub.add_parser("remove", help="remove a holding")
    p.add_argument("asset", type=asset_arg)

    chains = ("bitcoin", "ethereum", "solana")
    wallet = sub.add_parser("wallet", help="track blockchain wallets")
    wsub = wallet.add_subparsers(dest="action", required=True)
    wsub.add_parser("list")
    p = wsub.add_parser("add")
    p.add_argument("chain", choices=chains)
    p.add_argument("address")
    p.add_argument("--label", default="")
    p = wsub.add_parser("remove")
    p.add_argument("wallet_id")

    p = sub.add_parser("balance", help="look up any address without saving it")
    p.add_argument("chain", choices=chains)
    p.add_argument("address")

    p = sub.add_parser("web", help="start the web dashboard")
    p.add_argument("--host")
    p.add_argument("--port", type=int)

    sub.add_parser("gui", help="start the desktop app")
    return parser


COMMANDS = {
    "prices": cmd_prices,
    "portfolio": cmd_portfolio,
    "set": cmd_set,
    "add": cmd_add,
    "remove": cmd_remove,
    "wallet": cmd_wallet,
    "balance": cmd_balance,
}


def main(argv=None, service=None):
    args = build_parser().parse_args(argv)

    if args.command == "web":
        from .config import WEB_HOST, WEB_PORT
        from .web_app import start_web_app
        start_web_app(args.host or WEB_HOST, args.port or WEB_PORT)
        return 0

    if args.command == "gui":
        from .gui import start_gui
        start_gui()
        return 0

    from .service import GnomeFinance

    try:
        gf = service or GnomeFinance()
        COMMANDS.get(args.command or "portfolio")(gf, args)
    except GNOMEfinanceError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
