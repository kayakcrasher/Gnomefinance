from flask import Flask, jsonify

from .portfolio import Portfolio
from .prices import get_price
from .history import get_history


app = Flask(__name__)

portfolio = Portfolio()


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GNOMEfinance</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>GNOMEfinance</h1>
        <p>Web dashboard online.</p>

        <h2>Markets</h2>
        <div id="prices">Loading...</div>

        <script>
            async function loadPrices() {
                const response = await fetch("/api/prices");
                const data = await response.json();

                document.getElementById("prices").innerHTML =
                    `
                    <p>BTC: $${data.bitcoin}</p>
                    <p>ETH: $${data.ethereum}</p>
                    <p>SOL: $${data.solana}</p>
                    `;
            }

            loadPrices();
        </script>
    </body>
    </html>
    """


@app.route("/api/prices")
def prices():
    return jsonify(
        {
            "bitcoin": get_price("bitcoin"),
            "ethereum": get_price("ethereum"),
            "solana": get_price("solana"),
        }
    )


@app.route("/api/history/<coin_id>")
def history(coin_id):
    days = 7

    data = get_history(
        coin_id,
        days=days,
    )

    return jsonify(data)


@app.route("/api/portfolio")
def get_portfolio():
    return jsonify(
        portfolio.get_all_assets()
    )


def start_web_app():
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )


if __name__ == "__main__":
    start_web_app()
