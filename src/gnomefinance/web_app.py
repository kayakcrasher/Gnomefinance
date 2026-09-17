from flask import Flask, jsonify

from .portfolio import Portfolio
from .prices import get_price
from .history import get_history


app = Flask(__name__)

portfolio = Portfolio()


# ---------------------------------------------------------
# GNOMEFINANCE API
# ---------------------------------------------------------

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
        :root {
            --bg: #0b100d;
            --panel: #131b16;
            --panel-light: #19241d;
            --border: #2b3a30;
            --text: #edf2ed;
            --muted: #9aa89d;
            --gold: #d6b36a;
            --gold-light: #efd28c;
            --green: #83b889;
            --green-dark: #456b4b;
            --red: #c87878;
            --shadow: rgba(0, 0, 0, 0.35);
        }

        * {
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            margin: 0;
            min-height: 100vh;
            color: var(--text);
            font-family:
                Inter,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            background:
                radial-gradient(
                    circle at 15% 10%,
                    rgba(111, 148, 104, 0.12),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 85% 20%,
                    rgba(214, 179, 106, 0.08),
                    transparent 25%
                ),
                linear-gradient(
                    135deg,
                    #080c09,
                    #101710 45%,
                    #0a0f0b
                );
        }

        button {
            font: inherit;
        }

        /* -------------------------------------------------
           FOREST DECORATION
        ------------------------------------------------- */

        .forest-glow {
            position: fixed;
            inset: 0;
            pointer-events: none;
            overflow: hidden;
            z-index: -1;
        }

        .mushroom {
            position: absolute;
            opacity: 0.16;
            user-select: none;
        }

        .mushroom.one {
            left: 3%;
            bottom: 8%;
            font-size: 90px;
            transform: rotate(-8deg);
        }

        .mushroom.two {
            right: 5%;
            top: 18%;
            font-size: 65px;
            transform: rotate(10deg);
        }

        .mushroom.three {
            right: 15%;
            bottom: 4%;
            font-size: 45px;
        }

        /* -------------------------------------------------
           APP SHELL
        ------------------------------------------------- */

        .app {
            width: min(1400px, 94%);
            margin: 0 auto;
            padding: 24px 0 60px;
        }

        /* -------------------------------------------------
           HEADER
        ------------------------------------------------- */

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;

            padding: 22px 24px;
            margin-bottom: 18px;

            border: 1px solid var(--border);
            border-radius: 22px;

            background:
                linear-gradient(
                    145deg,
                    rgba(25, 36, 29, 0.94),
                    rgba(13, 19, 15, 0.96)
                );

            box-shadow: 0 18px 50px var(--shadow);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .gnome {
            width: 70px;
            height: 70px;

            display: grid;
            place-items: center;

            border-radius: 50%;
            border: 1px solid #5a5138;

            background:
                radial-gradient(
                    circle at 50% 30%,
                    #e4c37d 0 18%,
                    transparent 19%
                ),
                linear-gradient(
                    145deg,
                    #27372b,
                    #111811
                );

            font-size: 42px;
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.4);
        }

        .brand h1 {
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(1.8rem, 4vw, 2.5rem);
            letter-spacing: 0.03em;
        }

        .brand p {
            margin: 3px 0 0;
            color: var(--muted);
            font-size: 0.9rem;
        }

        .header-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        /* -------------------------------------------------
           BUTTONS
        ------------------------------------------------- */

        .btn {
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 10px 14px;

            color: var(--text);
            background: rgba(255, 255, 255, 0.035);

            cursor: pointer;
            transition:
                transform 0.15s ease,
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .btn:hover {
            transform: translateY(-1px);
            border-color: var(--gold);
            background: rgba(214, 179, 106, 0.08);
        }

        .btn-primary {
            color: #17140d;
            border-color: var(--gold);
            background: var(--gold);
            font-weight: 700;
        }

        .btn-primary:hover {
            background: var(--gold-light);
        }

        /* -------------------------------------------------
           NAVIGATION
        ------------------------------------------------- */

        .nav {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding: 8px;

            border: 1px solid var(--border);
            border-radius: 16px;

            background: rgba(12, 17, 13, 0.8);

            scrollbar-width: thin;
        }

        .nav button {
            flex: 0 0 auto;
            border: 0;
            border-radius: 10px;

            padding: 11px 16px;

            color: var(--muted);
            background: transparent;
            cursor: pointer;
        }

        .nav button:hover,
        .nav button.active {
            color: var(--text);
            background: var(--panel-light);
        }

        .nav button.active {
            box-shadow: inset 0 -2px 0 var(--gold);
        }

        /* -------------------------------------------------
           SECTIONS
        ------------------------------------------------- */

        .section {
            display: none;
            animation: fadeIn 0.2s ease;
        }

        .section.active {
            display: block;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(4px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .section-title {
            margin: 30px 0 14px;
        }

        .section-title h2 {
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.65rem;
        }

        .section-title p {
            margin: 5px 0 0;
            color: var(--muted);
        }

        /* -------------------------------------------------
           CARDS
        ------------------------------------------------- */

        .grid {
            display: grid;
            gap: 14px;
        }

        .grid-4 {
            grid-template-columns: repeat(4, 1fr);
        }

        .grid-3 {
            grid-template-columns: repeat(3, 1fr);
        }

        .grid-2 {
            grid-template-columns: repeat(2, 1fr);
        }

        .card {
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 20px;

            background:
                linear-gradient(
                    145deg,
                    rgba(24, 34, 27, 0.94),
                    rgba(15, 22, 17, 0.94)
                );

            box-shadow: 0 12px 35px var(--shadow);
        }

        .card-label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
        }

        .big-number {
            margin-top: 8px;
            font-size: clamp(1.5rem, 3vw, 2.1rem);
            font-weight: 750;
        }

        .positive {
            color: var(--green);
        }

        .negative {
            color: var(--red);
        }

        .gold {
            color: var(--gold-light);
        }

        /* -------------------------------------------------
           MARKET CARDS
        ------------------------------------------------- */

        .coin-card {
            position: relative;
            overflow: hidden;
        }

        .coin-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }

        .coin-name {
            font-weight: 700;
        }

        .coin-symbol {
            color: var(--muted);
            font-size: 0.78rem;
        }

        .coin-price {
            margin-top: 18px;
            font-size: 1.55rem;
            font-weight: 750;
        }

        .coin-change {
            margin-top: 5px;
            font-size: 0.9rem;
        }

        /* -------------------------------------------------
           LARGE FEATURE CARD
        ------------------------------------------------- */

        .hero-card {
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 20px;
            align-items: stretch;
        }

        .hero-main {
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .hero-eyebrow {
            color: var(--gold);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.13em;
        }

        .hero-title {
            margin: 10px 0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: clamp(2rem, 5vw, 3.4rem);
        }

        .hero-text {
            max-width: 650px;
            color: var(--muted);
            line-height: 1.6;
        }

        .hero-gnome {
            min-height: 250px;
            display: grid;
            place-items: center;

            border: 1px solid #3a4539;
            border-radius: 16px;

            background:
                radial-gradient(
                    circle,
                    rgba(214, 179, 106, 0.12),
                    transparent 65%
                );

            font-size: 130px;
        }

        /* -------------------------------------------------
           CHART PLACEHOLDER
        ------------------------------------------------- */

        .chart {
            min-height: 330px;

            display: flex;
            align-items: center;
            justify-content: center;

            border: 1px dashed #3a493d;
            border-radius: 14px;

            color: var(--muted);

            background:
                linear-gradient(
                    135deg,
                    rgba(20, 30, 23, 0.8),
                    rgba(9, 14, 10, 0.8)
                );
        }

        .chart-inner {
            text-align: center;
        }

        .chart-icon {
            font-size: 50px;
            margin-bottom: 8px;
        }

        /* -------------------------------------------------
           NEWS
        ------------------------------------------------- */

        .news-item {
            display: flex;
            justify-content: space-between;
            gap: 18px;

            padding: 17px 0;

            border-bottom: 1px solid var(--border);
        }

        .news-item:last-child {
            border-bottom: 0;
        }

        .news-title {
            margin: 0 0 5px;
            font-weight: 650;
        }

        .news-meta {
            color: var(--muted);
            font-size: 0.8rem;
        }

        .news-icon {
            flex: 0 0 auto;
            font-size: 26px;
        }

        /* -------------------------------------------------
           NETWORKS
        ------------------------------------------------- */

        .network-status {
            display: inline-flex;
            align-items: center;
            gap: 7px;

            color: var(--green);
            font-size: 0.85rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
        }

        /* -------------------------------------------------
           FOOTER
        ------------------------------------------------- */

        footer {
            margin-top: 35px;
            padding-top: 20px;

            border-top: 1px solid var(--border);

            color: var(--muted);
            text-align: center;
            font-size: 0.82rem;
        }

        /* -------------------------------------------------
           RESPONSIVE
        ------------------------------------------------- */

        @media (max-width: 1000px) {
            .grid-4 {
                grid-template-columns: repeat(2, 1fr);
            }

            .hero-card {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 650px) {
            .app {
                width: 94%;
                padding-top: 12px;
            }

            .header {
                align-items: flex-start;
                flex-direction: column;
            }

            .header-actions {
                width: 100%;
                justify-content: flex-start;
            }

            .grid-4,
            .grid-3,
            .grid-2 {
                grid-template-columns: 1fr;
            }

            .gnome {
                width: 58px;
                height: 58px;
                font-size: 34px;
            }

            .hero-gnome {
                min-height: 180px;
                font-size: 90px;
            }

            .news-item {
                flex-direction: column;
            }
        }
    </style>
</head>

<body>

<div class="forest-glow">
    <div class="mushroom one">🍄</div>
    <div class="mushroom two">🍄</div>
    <div class="mushroom three">🍄</div>
</div>

<div class="app">

    <!-- HEADER -->

    <header class="header">

        <div class="brand">
            <div class="gnome">🧙‍♂️</div>

            <div>
                <h1>GNOMEfinance</h1>
                <p>Your little corner of the financial forest.</p>
            </div>
        </div>

        <div class="header-actions">
            <button class="btn" onclick="refreshData()">
                🍄 Refresh
            </button>

            <button class="btn btn-primary" onclick="showSection('portfolio')">
                💰 Portfolio
            </button>
        </div>

    </header>


    <!-- NAVIGATION -->

    <nav class="nav">

        <button class="active" onclick="showSection('dashboard', this)">
            🏡 Dashboard
        </button>

        <button onclick="showSection('portfolio', this)">
            💰 Portfolio
        </button>

        <button onclick="showSection('markets', this)">
            📈 Markets
        </button>

        <button onclick="showSection('charts', this)">
            📊 Charts
        </button>

        <button onclick="showSection('news', this)">
            📰 News
        </button>

        <button onclick="showSection('networks', this)">
            🌐 Networks
        </button>

    </nav>


    <!-- =================================================
         DASHBOARD
    ================================================== -->

    <section id="dashboard" class="section active">

        <div class="section-title">
            <h2>Welcome back to the forest.</h2>
            <p>The gnome is watching the markets.</p>
        </div>


        <div class="card hero-card">

            <div class="hero-main">

                <div>
                    <div class="hero-eyebrow">
                        GNOMEfinance command center
                    </div>

                    <div class="hero-title">
                        Grow slow.<br>
                        Build something real.
                    </div>

                    <div class="hero-text">
                        Track your crypto, watch the markets, follow
                        your networks, and eventually connect the whole
                        forest to your DApp.
                    </div>
                </div>

                <div>
                    <button class="btn btn-primary"
                            onclick="showSection('markets')">
                        Explore Markets →
                    </button>
                </div>

            </div>

            <div class="hero-gnome">
                🧙‍♂️🍄
            </div>

        </div>


        <div class="section-title">
            <h2>Market Watch</h2>
            <p>A quick look at the coins we're tracking.</p>
        </div>


        <div id="dashboard-markets" class="grid grid-4">

            <div class="card coin-card">
                <div class="coin-top">
                    <div>
                        <div class="coin-name">Bitcoin</div>
                        <div class="coin-symbol">BTC</div>
                    </div>
                    <span>₿</span>
                </div>

                <div class="coin-price" id="btc-price">Loading...</div>
                <div class="coin-change">Waiting for market data</div>
            </div>


            <div class="card coin-card">
                <div class="coin-top">
                    <div>
                        <div class="coin-name">Ethereum</div>
                        <div class="coin-symbol">ETH</div>
                    </div>
                    <span>Ξ</span>
                </div>

                <div class="coin-price" id="eth-price">Loading...</div>
                <div class="coin-change">Waiting for market data</div>
            </div>


            <div class="card coin-card">
                <div class="coin-top">
                    <div>
                        <div class="coin-name">Solana</div>
                        <div class="coin-symbol">SOL</div>
                    </div>
                    <span>◎</span>
                </div>

                <div class="coin-price" id="sol-price">Loading...</div>
                <div class="coin-change">Waiting for market data</div>
            </div>


            <div class="card coin-card">
                <div class="coin-top">
                    <div>
                        <div class="coin-name">Cardano</div>
                        <div class="coin-symbol">ADA</div>
                    </div>
                    <span>₳</span>
                </div>

                <div class="coin-price" id="ada-price">Loading...</div>
                <div class="coin-change">Waiting for market data</div>
            </div>

        </div>

    </section>


    <!-- =================================================
         PORTFOLIO
    ================================================== -->

    <section id="portfolio" class="section">

        <div class="section-title">
            <h2>Portfolio</h2>
            <p>Your treasure chest.</p>
        </div>


        <div class="grid grid-4">

            <div class="card">
                <div class="card-label">Total Value</div>
                <div class="big-number gold" id="portfolio-total">
                    Loading...
                </div>
            </div>

            <div class="card">
                <div class="card-label">24h Change</div>
                <div class="big-number positive">
                    —
                </div>
            </div>

            <div class="card">
                <div class="card-label">BTC Allocation</div>
                <div class="big-number">
                    —
                </div>
            </div>

            <div class="card">
                <div class="card-label">Staking</div>
                <div class="big-number positive">
                    Active
                </div>
            </div>

        </div>


        <div class="section-title">
            <h2>Holdings</h2>
        </div>

        <div class="card" id="portfolio-holdings">
            <p class="muted">
                Portfolio data will appear here.
            </p>
        </div>

    </section>


    <!-- =================================================
         MARKETS
    ================================================== -->

    <section id="markets" class="section">

        <div class="section-title">
            <h2>Markets</h2>
            <p>The forest's market board.</p>
        </div>


        <div class="grid grid-3">

            <div class="card coin-card">
                <div class="coin-name">Bitcoin</div>
                <div class="coin-symbol">BTC</div>
                <div class="coin-price" id="market-btc">Loading...</div>
            </div>

            <div class="card coin-card">
                <div class="coin-name">Ethereum</div>
                <div class="coin-symbol">ETH</div>
                <div class="coin-price" id="market-eth">Loading...</div>
            </div>

            <div class="card coin-card">
                <div class="coin-name">Solana</div>
                <div class="coin-symbol">SOL</div>
                <div class="coin-price" id="market-sol">Loading...</div>
            </div>

            <div class="card coin-card">
                <div class="coin-name">Cardano</div>
                <div class="coin-symbol">ADA</div>
                <div class="coin-price" id="market-ada">Loading...</div>
            </div>

            <div class="card coin-card">
                <div class="coin-name">Avalanche</div>
                <div class="coin-symbol">AVAX</div>
                <div class="coin-price" id="market-avax">Loading...</div>
            </div>

            <div class="card coin-card">
                <div class="coin-name">Sui</div>
                <div class="coin-symbol">SUI</div>
                <div class="coin-price" id="market-sui">Loading...</div>
            </div>

        </div>

    </section>


    <!-- =================================================
         CHARTS
    ================================================== -->

    <section id="charts" class="section">

        <div class="section-title">
            <h2>Charts</h2>
            <p>Where the numbers start telling stories.</p>
        </div>


        <div class="card">

            <div class="header-actions">
                <button class="btn">24H</button>
                <button class="btn">7D</button>
                <button class="btn">30D</button>
                <button class="btn">1Y</button>
            </div>

            <br>

            <div class="chart">

                <div class="chart-inner">
                    <div class="chart-icon">📊</div>

                    <strong>Chart engine ready</strong>

                    <p>
                        Historical API data will be rendered here.
                    </p>
                </div>

            </div>

        </div>

    </section>


    <!-- =================================================
         NEWS
    ================================================== -->

    <section id="news" class="section">

        <div class="section-title">
            <h2>News from the Forest</h2>
            <p>Crypto headlines will live here.</p>
        </div>


        <div class="card">

            <div class="news-item">

                <div>
                    <p class="news-title">
                        🍄 News API connection coming next
                    </p>

                    <div class="news-meta">
                        GNOMEfinance • News feed
                    </div>
                </div>

                <div class="news-icon">
                    📰
                </div>

            </div>


            <div class="news-item">

                <div>
                    <p class="news-title">
                        Bitcoin, Solana, Cardano and more can be filtered here.
                    </p>

                    <div class="news-meta">
                        Ready for API integration
                    </div>
                </div>

                <div class="news-icon">
                    🌲
                </div>

            </div>

        </div>

    </section>


    <!-- =================================================
         NETWORKS
    ================================================== -->

    <section id="networks" class="section">

        <div class="section-title">
            <h2>Networks</h2>
            <p>The foundations of the future GNOMEfinance DApp.</p>
        </div>


        <div class="grid grid-3">

            <div class="card">

                <div class="coin-top">
                    <strong>Bitcoin</strong>

                    <span class="network-status">
                        <span class="status-dot"></span>
                        Ready
                    </span>
                </div>

                <p class="news-meta">
                    BTC network foundation
                </p>

            </div>


            <div class="card">

                <div class="coin-top">
                    <strong>Solana</strong>

                    <span class="network-status">
                        <span class="status-dot"></span>
                        Ready
                    </span>
                </div>

                <p class="news-meta">
                    SOL network foundation
                </p>

            </div>


            <div class="card">

                <div class="coin-top">
                    <strong>Cardano</strong>

                    <span class="network-status">
                        <span class="status-dot"></span>
                        Ready
                    </span>
                </div>

                <p class="news-meta">
                    ADA network foundation
                </p>

            </div>


            <div class="card">

                <div class="coin-top">
                    <strong>Avalanche</strong>

                    <span class="network-status">
                        <span class="status-dot"></span>
                        Ready
                    </span>
                </div>

                <p class="news-meta">
                    AVAX network foundation
                </p>

            </div>

        </div>

    </section>


    <footer>
        🍄 GNOMEfinance • Built one little piece at a time.
    </footer>

</div>


<script>

    // -----------------------------------------------------
    // NAVIGATION
    // -----------------------------------------------------

    function showSection(sectionId, button) {

        document.querySelectorAll(".section").forEach(section => {
            section.classList.remove("active");
        });

        const section = document.getElementById(sectionId);

        if (section) {
            section.classList.add("active");
        }

        document.querySelectorAll(".nav button").forEach(btn => {
            btn.classList.remove("active");
        });

        if (button) {
            button.classList.add("active");
        }
    }


    // -----------------------------------------------------
    // API HELPERS
    // -----------------------------------------------------

    async function loadPrices() {

        try {

            const response = await fetch("/api/prices");

            if (!response.ok) {
                throw new Error("Price API returned an error.");
            }

            const data = await response.json();

            updatePrices(data);

        } catch (error) {

            console.error("GNOMEfinance price error:", error);

            setText("btc-price", "Unavailable");
            setText("eth-price", "Unavailable");
            setText("sol-price", "Unavailable");
            setText("ada-price", "Unavailable");

            setText("market-btc", "Unavailable");
            setText("market-eth", "Unavailable");
            setText("market-sol", "Unavailable");
            setText("market-ada", "Unavailable");
            setText("market-avax", "Unavailable");
            setText("market-sui", "Unavailable");
        }
    }


    function updatePrices(data) {

        const lookup = {
            btc: ["btc-price", "market-btc"],
            bitcoin: ["btc-price", "market-btc"],

            eth: ["eth-price", "market-eth"],
            ethereum: ["eth-price", "market-eth"],

            sol: ["sol-price", "market-sol"],
            solana: ["sol-price", "market-sol"],

            ada: ["ada-price", "market-ada"],
            cardano: ["ada-price", "market-ada"],

            avax: ["market-avax"],
            avalanche: ["market-avax"],

            sui: ["market-sui"]
        };

        Object.keys(data || {}).forEach(key => {

            const value = data[key];

            const targets = lookup[key.toLowerCase()];

            if (!targets) {
                return;
            }

            targets.forEach(target => {
                setText(target, formatPrice(value));
            });
        });
    }


    function formatPrice(value) {

        if (typeof value === "number") {
            return "$" + value.toLocaleString(
                undefined,
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 8
                }
            );
        }

        if (value && typeof value === "object") {

            if (typeof value.usd === "number") {
                return "$" + value.usd.toLocaleString(
                    undefined,
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 8
                    }
                );
            }

            if (typeof value.price === "number") {
                return "$" + value.price.toLocaleString(
                    undefined,
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 8
                    }
                );
            }
        }

        return String(value);
    }


    function setText(id, value) {

        const element = document.getElementById(id);

        if (element) {
            element.textContent = value;
        }
    }


    // -----------------------------------------------------
    // PORTFOLIO
    // -----------------------------------------------------

    async function loadPortfolio() {

        try {

            const response = await fetch("/api/portfolio");

            if (!response.ok) {
                throw new Error("Portfolio API returned an error.");
            }

            const data = await response.json();

            renderPortfolio(data);

        } catch (error) {

            console.error(
                "GNOMEfinance portfolio error:",
                error
            );
        }
    }


    function renderPortfolio(data) {

        if (!data) {
            return;
        }

        const total =
            data.total_value ??
            data.total ??
            data.value;

        if (total !== undefined) {
            setText(
                "portfolio-total",
                formatPrice(total)
            );
        }

        const holdings =
            data.holdings ??
            data.assets ??
            data;

        const container =
            document.getElementById("portfolio-holdings");

        if (!container || typeof holdings !== "object") {
            return;
        }

        if (Array.isArray(holdings)) {

            container.innerHTML =
                holdings.map(item => {

                    const name =
                        item.name ??
                        item.symbol ??
                        "Asset";

                    const amount =
                        item.amount ??
                        item.quantity ??
                        "";

                    return `
                        <div class="news-item">
                            <div>
                                <strong>${name}</strong>
                            </div>
                            <div class="gold">
                                ${amount}
                            </div>
                        </div>
                    `;

                }).join("");

        }

    }


    // -----------------------------------------------------
    // REFRESH
    // -----------------------------------------------------

    async function refreshData() {

        await Promise.all([
            loadPrices(),
            loadPortfolio()
        ]);

    }


    // -----------------------------------------------------
    // STARTUP
    // -----------------------------------------------------

    document.addEventListener(
        "DOMContentLoaded",
        () => {
            refreshData();
        }
    );

</script>

</body>
</html>
"""


# ---------------------------------------------------------
# PRICE API
# ---------------------------------------------------------

@app.route("/api/prices")
def prices():

    coins = [
        "bitcoin",
        "ethereum",
        "solana",
        "cardano",
        "avalanche-2",
        "sui"
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


# ---------------------------------------------------------
# HISTORY API
# ---------------------------------------------------------

@app.route("/api/history/<coin_id>")
def history(coin_id):

    try:

        data = get_history(coin_id)

        return jsonify(data)

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# PORTFOLIO API
# ---------------------------------------------------------

@app.route("/api/portfolio")
def portfolio_data():

    try:

        data = portfolio.get_data()

        return jsonify(data)

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500
