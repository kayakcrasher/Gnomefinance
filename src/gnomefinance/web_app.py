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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>GNOMEfinance</title>

    <style>
        * {
            box-sizing: border-box;
        }

        :root {
            --bg: #0b0f0c;
            --surface: #121914;
            --surface-2: #18211a;
            --border: #29362c;
            --text: #f1f0e8;
            --muted: #98a197;
            --gold: #d5b56a;
            --gold-soft: #ead08b;
            --green: #8bb98c;
        }

        body {
            margin: 0;
            min-height: 100vh;
            color: var(--text);
            background:
                radial-gradient(
                    circle at 15% 10%,
                    rgba(95, 126, 91, 0.18),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 90% 85%,
                    rgba(213, 181, 106, 0.08),
                    transparent 25%
                ),
                var(--bg);

            font-family:
                Inter,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        /* ---------- PAGE ---------- */

        .page {
            width: min(1180px, 92%);
            margin: auto;
            padding: 28px 0 50px;
        }

        /* ---------- HEADER ---------- */

        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;

            padding: 22px 24px;
            margin-bottom: 18px;

            border: 1px solid var(--border);
            border-radius: 20px;

            background:
                linear-gradient(
                    145deg,
                    rgba(24, 33, 26, 0.96),
                    rgba(14, 19, 15, 0.96)
                );

            box-shadow:
                0 20px 50px rgba(0, 0, 0, 0.28);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .gnome {
            width: 66px;
            height: 66px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle at 50% 38%,
                    #e0c99a 0 18%,
                    transparent 19%
                ),
                linear-gradient(
                    145deg,
                    #40513d,
                    #182119
                );

            border: 1px solid #4c5947;

            font-size: 40px;

            box-shadow:
                inset 0 0 25px rgba(0, 0, 0, 0.35),
                0 8px 25px rgba(0, 0, 0, 0.25);
        }

        h1 {
            margin: 0;

            font-family:
                Georgia,
                "Times New Roman",
                serif;

            font-size: clamp(1.8rem, 5vw, 2.5rem);
            letter-spacing: 0.02em;
        }

        .tagline {
            margin: 4px 0 0;
            color: var(--muted);
            font-size: 0.9rem;
        }

        /* ---------- BUTTONS ---------- */

        .actions {
            display: flex;
            gap: 9px;
        }

        button {
            border: 1px solid var(--border);
            border-radius: 11px;

            padding: 10px 15px;

            color: var(--text);
            background: rgba(255, 255, 255, 0.035);

            cursor: pointer;

            transition:
                transform 0.15s ease,
                border-color 0.15s ease,
                background 0.15s ease;
        }

        button:hover {
            transform: translateY(-1px);
            border-color: var(--gold);
            background: rgba(213, 181, 106, 0.08);
        }

        .refresh {
            color: #17140d;
            background: var(--gold);
            border-color: var(--gold);
            font-weight: 700;
        }

        .refresh:hover {
            background: var(--gold-soft);
        }

        /* ---------- HERO ---------- */

        .hero {
            position: relative;
            overflow: hidden;

            min-height: 300px;

            display: flex;
            align-items: center;

            padding: 38px;

            margin-bottom: 18px;

            border: 1px solid var(--border);
            border-radius: 22px;

            background:
                linear-gradient(
                    120deg,
                    rgba(27, 39, 29, 0.98),
                    rgba(14, 20, 15, 0.97)
                );

            box-shadow:
                0 20px 55px rgba(0, 0, 0, 0.3);
        }

        .hero-content {
            max-width: 650px;
            position: relative;
            z-index: 2;
        }

        .eyebrow {
            color: var(--gold);
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .hero h2 {
            margin: 10px 0 12px;

            font-family:
                Georgia,
                "Times New Roman",
                serif;

            font-size: clamp(2rem, 6vw, 3.6rem);
            line-height: 1.05;
        }

        .hero p {
            max-width: 580px;
            color: var(--muted);
            line-height: 1.65;
        }

        .hero-mushrooms {
            position: absolute;
            right: 30px;
            bottom: 12px;

            font-size: 100px;
            opacity: 0.25;

            transform: rotate(-4deg);
        }

        /* ---------- SECTION TITLE ---------- */

        .section-heading {
            display: flex;
            align-items: end;
            justify-content: space-between;

            margin: 30px 2px 13px;
        }

        .section-heading h2 {
            margin: 0;

            font-family:
                Georgia,
                "Times New Roman",
                serif;

            font-size: 1.55rem;
        }

        .section-heading span {
            color: var(--muted);
            font-size: 0.85rem;
        }

        /* ---------- CARDS ---------- */

        .cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 13px;
        }

        .card {
            padding: 19px;

            border: 1px solid var(--border);
            border-radius: 17px;

            background:
                linear-gradient(
                    145deg,
                    rgba(24, 33, 26, 0.95),
                    rgba(15, 21, 16, 0.95)
                );

            box-shadow:
                0 10px 30px rgba(0, 0, 0, 0.2);

            transition:
                transform 0.15s ease,
                border-color 0.15s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            border-color: #3d4b3f;
        }

        .card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .coin {
            font-weight: 700;
        }

        .symbol {
            margin-top: 3px;
            color: var(--muted);
            font-size: 0.75rem;
        }

        .coin-icon {
            color: var(--gold);
            font-size: 1.35rem;
        }

        .price {
            margin-top: 22px;

            font-size: 1.55rem;
            font-weight: 750;
        }

        .status {
            margin-top: 6px;
            color: var(--green);
            font-size: 0.78rem;
        }

        /* ---------- LOWER PANELS ---------- */

        .lower {
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 13px;
        }

        .panel {
            min-height: 190px;
            padding: 21px;

            border: 1px solid var(--border);
            border-radius: 17px;

            background: var(--surface);
        }

        .panel h3 {
            margin: 0 0 8px;

            font-family:
                Georgia,
                "Times New Roman",
                serif;

            font-size: 1.25rem;
        }

        .panel p {
            color: var(--muted);
            line-height: 1.55;
        }

        .panel-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 9px;
            margin-top: 18px;
        }

        /* ---------- FOOTER ---------- */

        footer {
            margin-top: 35px;

            color: var(--muted);
            text-align: center;

            font-size: 0.78rem;
        }

        /* ---------- MOBILE ---------- */

        @media (max-width: 850px) {

            header {
                align-items: flex-start;
                flex-direction: column;
            }

            .actions {
                width: 100%;
            }

            .actions button {
                flex: 1;
            }

            .cards {
                grid-template-columns: repeat(2, 1fr);
            }

            .lower {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 520px) {

            .page {
                width: 94%;
                padding-top: 14px;
            }

            .hero {
                padding: 27px;
                min-height: 280px;
            }

            .hero-mushrooms {
                right: -10px;
                font-size: 80px;
            }

            .cards {
                grid-template-columns: 1fr;
            }

            .gnome {
                width: 58px;
                height: 58px;
                font-size: 34px;
            }
        }
    </style>
</head>

<body>

<div class="page">

    <!-- HEADER -->

    <header>

        <div class="brand">

            <div class="gnome">
                🧙‍♂️
            </div>

            <div>
                <h1>GNOMEfinance</h1>
                <div class="tagline">
                    Crypto tools from a little corner of the forest.
                </div>
            </div>

        </div>

        <div class="actions">

            <button class="refresh" onclick="location.reload()">
                🍄 Refresh
            </button>

        </div>

    </header>


    <!-- HERO -->

    <section class="hero">

        <div class="hero-content">

            <div class="eyebrow">
                Welcome to the forest
            </div>

            <h2>
                Watch your treasure grow.
            </h2>

            <p>
                GNOMEfinance is your personal crypto command center —
                simple, clean, and built one little piece at a time.
            </p>

            <button onclick="document
                .getElementById('markets')
                .scrollIntoView({ behavior: 'smooth' })">
                Explore the markets →
            </button>

        </div>

        <div class="hero-mushrooms">
            🍄 🍄
        </div>

    </section>


    <!-- MARKET SECTION -->

    <div class="section-heading">

        <h2>Market Watch</h2>

        <span>
            Live data from your existing API
        </span>

    </div>


    <section class="cards" id="markets">

        <div class="card">

            <div class="card-top">

                <div>
                    <div class="coin">Bitcoin</div>
                    <div class="symbol">BTC</div>
                </div>

                <div class="coin-icon">₿</div>

            </div>

            <div class="price" id="btc-price">
                Loading...
            </div>

            <div class="status">
                ● Market data
            </div>

        </div>


        <div class="card">

            <div class="card-top">

                <div>
                    <div class="coin">Ethereum</div>
                    <div class="symbol">ETH</div>
                </div>

                <div class="coin-icon">Ξ</div>

            </div>

            <div class="price" id="eth-price">
                Loading...
            </div>

            <div class="status">
                ● Market data
            </div>

        </div>


        <div class="card">

            <div class="card-top">

                <div>
                    <div class="coin">Solana</div>
                    <div class="symbol">SOL</div>
                </div>

                <div class="coin-icon">◎</div>

            </div>

            <div class="price" id="sol-price">
                Loading...
            </div>

            <div class="status">
                ● Market data
            </div>

        </div>


        <div class="card">

            <div class="card-top">

                <div>
                    <div class="coin">Cardano</div>
                    <div class="symbol">ADA</div>
                </div>

                <div class="coin-icon">₳</div>

            </div>

            <div class="price" id="ada-price">
                Loading...
            </div>

            <div class="status">
                ● Market data
            </div>

        </div>

    </section>


    <!-- LOWER PANELS -->

    <div class="section-heading">

        <h2>GNOME's Workbench</h2>

        <span>
            More tools coming soon
        </span>

    </div>


    <section class="lower">

        <div class="panel">

            <h3>🍄 Portfolio</h3>

            <p>
                Your holdings, allocation, staking, and performance
                will live here as we build the next layer.
            </p>

            <div class="panel-buttons">

                <button>
                    View Portfolio
                </button>

                <button>
                    Staking
                </button>

            </div>

        </div>


        <div class="panel">

            <h3>🌲 Networks</h3>

            <p>
                The foundation for the eventual GNOMEfinance DApp.
            </p>

            <div class="panel-buttons">

                <button>
                    Bitcoin
                </button>

                <button>
                    Solana
                </button>

                <button>
                    Cardano
                </button>

            </div>

        </div>

    </section>


    <footer>
        🍄 GNOMEfinance — built one block at a time.
    </footer>

</div>


<script>

    async function loadPrices() {

        try {

            const response =
                await fetch("/api/prices");

            if (!response.ok) {
                throw new Error("Price request failed");
            }

            const data =
                await response.json();

            updatePrice(
                "btc-price",
                data.bitcoin
            );

            updatePrice(
                "eth-price",
                data.ethereum
            );

            updatePrice(
                "sol-price",
                data.solana
            );

            updatePrice(
                "ada-price",
                data.cardano
            );

        } catch (error) {

            console.error(
                "GNOMEfinance price error:",
                error
            );

            document.getElementById(
                "btc-price"
            ).textContent = "Unavailable";

            document.getElementById(
                "eth-price"
            ).textContent = "Unavailable";

            document.getElementById(
                "sol-price"
            ).textContent = "Unavailable";

            document.getElementById(
                "ada-price"
            ).textContent = "Unavailable";
        }
    }


    function updatePrice(elementId, value) {

        const element =
            document.getElementById(elementId);

        if (!element) {
            return;
        }

        if (
            typeof value === "number"
        ) {

            element.textContent =
                "$" +
                value.toLocaleString(
                    undefined,
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 8
                    }
                );

            return;
        }

        if (
            value &&
            typeof value === "object" &&
            typeof value.usd === "number"
        ) {

            element.textContent =
                "$" +
                value.usd.toLocaleString(
                    undefined,
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 8
                    }
                );

            return;
        }

        element.textContent =
            String(value ?? "Unavailable");
    }


    document.addEventListener(
        "DOMContentLoaded",
        loadPrices
    );

</script>

</body>
</html>
"""


@app.route("/api/prices")
def prices():

    coins = [
        "bitcoin",
        "ethereum",
        "solana",
    ]

    result = {}

    for coin in coins:

        try:
            result[coin] = get_price(coin)

        except Exception as error:

            result[coin] = {
                "error": str(error)
            }

    return jsonify(result)


@app.route("/api/history/<coin_id>")
def history(coin_id):

    try:

        data = get_history(coin_id)

        return jsonify(data)

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/portfolio")
def portfolio_data():

    try:

        data = portfolio.get_data()

        return jsonify(data)

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500
