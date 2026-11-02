"""GNOMEfinance web dashboard (Flask).

The page itself is templates/index.html; it calls the JSON API below.
"""

from flask import Flask, jsonify, render_template, request

from . import __version__
from .assets import ASSETS
from .config import WEB_HOST, WEB_PORT
from .errors import APIError, GNOMEfinanceError, NetworkError, ValidationError
from .market import HISTORY_RANGES
from .service import GnomeFinance


def create_app(service=None):
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # Created lazily so importing this module never touches disk or network.
    state = {"service": service}

    def gf():
        if state["service"] is None:
            state["service"] = GnomeFinance()
        return state["service"]

    def wants_refresh():
        return request.args.get("refresh") in ("1", "true", "yes")

    def json_body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ValidationError("Expected a JSON object.")
        return data

    # -- Errors ------------------------------------------------------------

    @app.errorhandler(ValidationError)
    def bad_request(error):
        return jsonify(error=str(error)), 400

    @app.errorhandler(NetworkError)
    @app.errorhandler(APIError)
    def upstream_error(error):
        return jsonify(error=str(error)), 502

    @app.errorhandler(GNOMEfinanceError)
    def app_error(error):
        return jsonify(error=str(error)), 500

    # -- Pages -------------------------------------------------------------

    @app.get("/")
    def home():
        return render_template(
            "index.html",
            version=__version__,
            assets=ASSETS,
            chains=gf().chains,
            ranges=HISTORY_RANGES,
            static_site=app.config.get("STATIC_SITE", False),
        )

    # -- API ---------------------------------------------------------------

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", version=__version__)

    @app.get("/api/assets")
    def list_assets():
        return jsonify(ASSETS)

    @app.get("/api/market")
    def market():
        return jsonify(gf().quotes(force=wants_refresh()))

    @app.get("/api/history/<asset_id>")
    def history(asset_id):
        days = request.args.get("days", 7)
        try:
            days = int(days)
        except ValueError:
            raise ValidationError("days must be a whole number.") from None
        return jsonify(gf().history(asset_id, days))

    @app.get("/api/portfolio")
    def portfolio():
        return jsonify(gf().summary(force=wants_refresh()))

    @app.put("/api/holdings/<asset_id>")
    def set_holding(asset_id):
        gf().set_holding(asset_id, json_body().get("amount"))
        return jsonify(gf().portfolio.holdings)

    @app.delete("/api/holdings/<asset_id>")
    def remove_holding(asset_id):
        gf().remove_holding(asset_id)
        return jsonify(gf().portfolio.holdings)

    @app.delete("/api/holdings")
    def clear_holdings():
        gf().clear_holdings()
        return jsonify({})

    @app.get("/api/wallets")
    def list_wallets():
        return jsonify(gf().wallet_balances(force=wants_refresh()))

    @app.post("/api/wallets")
    def add_wallet():
        data = json_body()
        wallet = gf().add_wallet(
            data.get("chain", ""), data.get("address", ""), data.get("label", "")
        )
        return jsonify(wallet), 201

    @app.delete("/api/wallets/<wallet_id>")
    def remove_wallet(wallet_id):
        gf().remove_wallet(wallet_id)
        return "", 204

    @app.get("/api/balance/<chain_id>/<address>")
    def balance(chain_id, address):
        return jsonify(
            chain=chain_id,
            address=address,
            balance=gf().lookup_balance(chain_id, address),
        )

    return app


def start_web_app(host=WEB_HOST, port=WEB_PORT, debug=False):
    print(f"GNOMEfinance running at http://{host}:{port}")
    create_app().run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    start_web_app()
