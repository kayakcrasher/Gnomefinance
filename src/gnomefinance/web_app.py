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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>GNOMEfinance</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                min-height: 100vh;
                font-family: Georgia, "Times New Roman", serif;
                background:
                    linear-gradient(
                        rgba(20, 35, 24, 0.94),
                        rgba(13, 25, 17, 0.98)
                    );
                color: #f1e7cf;
            }

            .forest {
                min-height: 100vh;
                padding: 18px;
            }

            .container {
                width: 100%;
                max-width: 900px;
                margin: 0 auto;
            }

            .header {
                padding: 22px;
                border: 1px solid #695437;
                border-radius: 18px;
                background: #293b29;
                box-shadow:
                    0 8px 25px rgba(0, 0, 0, 0.35);
                margin-bottom: 18px;
            }

            .brand {
                display: flex;
                align-items: center;
                gap: 14px;
            }

            .gnome {
                font-size: 48px;
            }

            h1 {
                margin: 0;
                font-size: 30px;
                color: #f3d99b;
            }

            .subtitle {
                margin-top: 5px;
                color: #b9c6a7;
                font-size: 14px;
            }

            .section-title {
                margin: 24px 4px 10px;
                color: #dfc58e;
                font-size: 20px;
            }

            .card {
                background: #344732;
                border: 1px solid #695437;
                border-radius: 16px;
                padding: 18px;
                margin-bottom: 12px;
                box-shadow:
                    0 5px 16px rgba(0, 0, 0, 0.25);
            }

            .market-grid {
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(140px, 1fr));
                gap: 12px;
            }

            .coin {
                background: #243523;
                border: 1px solid #596746;
                border-radius: 14px;
                padding: 16px;
            }

            .coin-name {
                color: #b8c7a8;
                font-size: 13px;
                margin-bottom: 8px;
            }

            .coin-price {
                color: #f4dfaa;
                font-size: 20px;
                font-weight: bold;
            }

            .status {
                text-align: center;
                color: #aebda0;
                font-size: 13px;
                margin-top: 20px;
            }

            .wood-divider {
                height: 2px;
                margin: 20px 0;
                background: #695437;
                opacity: 0.7;
            }

            .footer {
                text-align: center;
                padding: 24px 10px;
                color: #7f9178;
                font-size: 12px;
            }

            .loading {
                color: #b8c7a8;
            }

            .error {
                color: #d99b7c;
            }
        </style>
    </head>

    <body>
        <div class="forest">
            <div class="container">

                <header class="header">
                    <div class="brand">
                        <div class="gnome">🧙‍♂️</div>

                        <div>
                            <h1>GNOMEfinance</h1>
                            <div class="subtitle">
                                Your little corner of the financial forest.
                            </div>
                        </div>
                    </div>
                </header>

                <div class="section-title">
                    🌲 Market Watch
                </div>

                <section class="card">
                    <div
                        id="prices"
                        class="market-grid"
                    >
                        <div class="coin">
                            <div class="coin-name">
                                Loading the forest...
                            </div>
                            <div class="coin-price loading">
                                ⏳
                            </div>
                        </div>
                    </div>
                </section>

                <div class="section-title">
                    🪵 Portfolio
                </div>

                <section class="card">
                    <div id="portfolio">
                        Loading portfolio...
                    </div>
                </section>

                <div class="wood-divider"></div>

                <div class="status" id="status">
                    GNOMEfinance is tending the garden...
                </div>

                <footer class="footer">
                    🌿 Built in the GNOMEfinance woodland 🌿
                </footer>

            </div>
        </div>

        <script>
            async function loadPrices() {
                const prices = document.getElementById("prices");

                try {
                    const response =
                        await fetch("/api/prices");

                    if (!response.ok) {
                        throw new Error("Price request failed");
                    }

                    const data = await response.json();

                    prices.innerHTML = `
                        <div class="coin">
                            <div class="coin-name">₿ Bitcoin</div>
                            <div class="coin-price">
                                $${Number(data.bitcoin).toLocaleString(
                                    undefined,
                                    {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    }
                                )}
                            </div>
                        </div>

                        <div class="coin">
                            <div class="coin-name">Ξ Ethereum</div>
                            <div class="coin-price">
                                $${Number(data.ethereum).toLocaleString(
                                    undefined,
                                    {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    }
                                )}
                            </div>
                        </div>

                        <div class="coin">
                            <div class="coin-name">◎ Solana</div>
                            <div class="coin-price">
                                $${Number(data.solana).toLocaleString(
                                    undefined,
                                    {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    }
                                )}
                            </div>
                        </div>
                    `;

                    document.getElementById("status").textContent =
                        "🌿 Market data gathered successfully.";
                } catch (error) {
                    prices.innerHTML = `
                        <div class="error">
                            The forest spirits could not reach the market.
                        </div>
                    `;

                    document.getElementById("status").textContent =
                        "⚠️ Market data unavailable.";
                }
            }


            async function loadPortfolio() {
                const portfolio =
                    document.getElementById("portfolio");

                try {
                    const response =
                        await fetch("/api/portfolio");

                    const data = await response.json();

                    const assets = Object.entries(data);

                    if (assets.length === 0) {
                        portfolio.innerHTML = `
                            <div class="loading">
                                🌱 Your portfolio garden is empty.
                            </div>
                        `;
                        return;
                    }

                    portfolio.innerHTML = assets.map(
                        ([network, amount]) => `
                            <div class="coin">
                                <div class="coin-name">
                                    ${network}
                                </div>
                                <div class="coin-price">
                                    ${amount}
                                </div>
                            </div>
                        `
                    ).join("");
                } catch (error) {
                    portfolio.innerHTML = `
                        <div class="error">
                            Could not load the portfolio.
                        </div>
                    `;
                }
            }


            loadPrices();
            loadPortfolio();
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
    data = get_history(
        coin_id,
        days=7,
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
