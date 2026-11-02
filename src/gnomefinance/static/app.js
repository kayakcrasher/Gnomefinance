// GNOMEfinance dashboard: talks to the Flask JSON API and draws the page.

const $ = (id) => document.getElementById(id);

const PALETTE = ["#d5b56a", "#8bb98c", "#7fa3c9", "#c48fb8", "#d98a7e", "#9fb3a3"];

const state = {
    chartAsset: "bitcoin",
    chartDays: 7,
    summary: null,
};

// ---------- Formatting ----------

function usd(value) {
    if (value === null || value === undefined) return "—";
    const abs = Math.abs(value);
    const digits = abs >= 1 ? 2 : abs >= 0.01 ? 4 : 6;
    return value.toLocaleString(undefined, {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
    });
}

function amount(value) {
    // Big numbers don't need satoshi-level precision on screen.
    const abs = Math.abs(value);
    const digits = abs >= 1000 ? 2 : abs >= 1 ? 4 : 8;
    return value.toLocaleString(undefined, { maximumFractionDigits: digits });
}

function pct(value) {
    const sign = value > 0 ? "+" : "";
    return `${sign}${value.toFixed(2)}%`;
}

function trendClass(value) {
    return value > 0 ? "up" : value < 0 ? "down" : "muted";
}

function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
        if (key === "class") node.className = value;
        else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
        else node.setAttribute(key, value);
    }
    for (const child of children) {
        if (child === null || child === undefined) continue;
        node.append(child instanceof Node ? child : String(child));
    }
    return node;
}

// ---------- API ----------

async function api(path, options = {}) {
    // On GitHub Pages there is no server: browser_backend.js answers instead.
    if (window.GnomeBackend) return window.GnomeBackend.request(path, options);

    const response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (response.status === 204) return null;
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    return data;
}

let toastTimer;
function toast(message, isError = false) {
    const box = $("toast");
    box.textContent = message;
    box.classList.toggle("error", isError);
    box.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (box.hidden = true), 3500);
}

// ---------- Market cards ----------

function renderMarket(quotes) {
    document.querySelectorAll(".card[data-asset]").forEach((card) => {
        const quote = quotes[card.dataset.asset];
        const price = card.querySelector('[data-field="price"]');
        const change = card.querySelector('[data-field="change"]');

        if (!quote) {
            price.textContent = "Unavailable";
            change.textContent = "";
            return;
        }
        price.textContent = usd(quote.price);
        change.textContent = `${pct(quote.change_24h)} 24h`;
        change.className = `change ${trendClass(quote.change_24h)}`;
    });
}

// ---------- Portfolio ----------

function renderSummary(summary) {
    state.summary = summary;

    $("total-value").textContent = usd(summary.total_value);

    const change = $("total-change");
    if (summary.assets.length === 0) {
        change.textContent = "Add holdings or a wallet below to get started.";
        change.className = "hero-change";
    } else {
        change.textContent =
            `${summary.change_24h >= 0 ? "+" : "−"}${usd(Math.abs(summary.change_24h))}` +
            ` (${pct(summary.change_24h_pct)}) today`;
        change.className = `hero-change ${trendClass(summary.change_24h)}`;
    }

    // Allocation bar + legend
    const bar = $("alloc-bar");
    const legend = $("alloc-legend");
    bar.replaceChildren();
    legend.replaceChildren();
    summary.assets
        .filter((a) => a.allocation > 0)
        .forEach((a, i) => {
            const color = PALETTE[i % PALETTE.length];
            bar.append(el("span", {
                style: `width:${a.allocation}%;background:${color}`,
                title: `${a.symbol} ${a.allocation.toFixed(1)}%`,
            }));
            legend.append(el("span", {}, el("i", { style: `background:${color}` }),
                `${a.symbol} ${a.allocation.toFixed(1)}%`));
        });

    // Warnings (offline API, failed wallet lookups...)
    const notes = [...summary.errors];
    if (summary.prices_stale) notes.unshift("Showing last known prices — the market API is not responding.");
    $("notice").hidden = notes.length === 0;
    $("notice").textContent = notes.join(" · ");

    renderHoldings(summary.assets);
    renderWallets(summary.wallets);
}

function renderHoldings(rows) {
    const body = $("holdings");
    body.replaceChildren();

    if (rows.length === 0) {
        body.append(el("tr", {}, el("td", { colspan: 6, class: "empty" }, "No holdings yet.")));
        return;
    }

    for (const row of rows) {
        const parts = [];
        if (row.manual_amount) parts.push(`${amount(row.manual_amount)} manual`);
        if (row.wallet_amount) parts.push(`${amount(row.wallet_amount)} in ${row.wallet_count} wallet${row.wallet_count === 1 ? "" : "s"}`);

        const remove = row.manual_amount
            ? el("button", {
                class: "icon-btn",
                title: `Remove manual ${row.symbol}`,
                "aria-label": `Remove manual ${row.symbol}`,
                onclick: () => removeHolding(row.asset_id, row.symbol),
            }, "✕")
            : "";

        body.append(el("tr", {},
            el("td", {}, `${row.icon} ${row.symbol}`, el("small", {}, row.price !== null ? usd(row.price) : "no price")),
            el("td", { class: "num" }, amount(row.amount), parts.length > 1 ? el("small", {}, parts.join(" + ")) : row.wallet_amount ? el("small", {}, "on-chain") : null),
            el("td", { class: "num" }, usd(row.value)),
            el("td", { class: `num ${trendClass(row.change_24h)}` }, pct(row.change_24h)),
            el("td", { class: "num" }, `${row.allocation.toFixed(1)}%`),
            el("td", { class: "num" }, remove),
        ));
    }
}

function renderWallets(wallets) {
    const list = $("wallets");
    list.replaceChildren();

    if (wallets.length === 0) {
        list.append(el("li", { class: "empty" }, "No wallets tracked yet."));
        return;
    }

    for (const w of wallets) {
        const balance = w.balance === null
            ? el("span", { class: "wallet-err" }, "unavailable")
            : `${amount(w.balance)} ${w.symbol}`;

        list.append(el("li", {},
            el("div", { class: "wallet-info" },
                el("div", { class: "wallet-label" }, w.label),
                el("a", { class: "wallet-addr", href: w.explorer_url, target: "_blank", rel: "noopener", title: w.address }, w.address),
                w.error ? el("div", { class: "wallet-err" }, w.error) : null,
            ),
            el("div", { class: "wallet-bal" },
                balance,
                el("button", {
                    class: "icon-btn",
                    title: "Stop tracking",
                    "aria-label": `Stop tracking ${w.label}`,
                    onclick: () => removeWallet(w),
                }, "✕"),
            ),
        ));
    }
}

// ---------- Chart ----------

function selectChartAsset(assetId) {
    state.chartAsset = assetId;
    document.querySelectorAll(".card[data-asset]").forEach((card) =>
        card.classList.toggle("selected", card.dataset.asset === assetId));
    loadChart();
}

async function loadChart() {
    const card = document.querySelector(`.card[data-asset="${state.chartAsset}"]`);
    $("chart-title").textContent = card ? card.querySelector(".coin").textContent : state.chartAsset;
    const box = $("chart");
    const wanted = `${state.chartAsset}:${state.chartDays}`;

    try {
        const points = await api(`/api/history/${state.chartAsset}?days=${state.chartDays}`);
        // Ignore slow answers for a chart the user already switched away from.
        if (wanted !== `${state.chartAsset}:${state.chartDays}`) return;
        drawChart(box, points);
    } catch (error) {
        box.replaceChildren(el("div", { class: "chart-empty" }, `Chart unavailable: ${error.message}`));
        $("chart-stats").textContent = " ";
    }
}

function drawChart(box, points) {
    if (points.length < 2) {
        box.replaceChildren(el("div", { class: "chart-empty" }, "Not enough data yet."));
        return;
    }

    const prices = points.map((p) => p[1]);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const first = prices[0];
    const last = prices[prices.length - 1];
    const change = ((last - first) / first) * 100;

    const stats = $("chart-stats");
    stats.replaceChildren(
        `Low ${usd(min)} · High ${usd(max)} · `,
        el("span", { class: trendClass(change) }, `${pct(change)} over this range`),
    );

    const W = 1000, H = 280, PAD_T = 12, PAD_B = 12;
    const span = max - min || 1;
    const x = (i) => (i / (points.length - 1)) * W;
    const y = (p) => PAD_T + (1 - (p - min) / span) * (H - PAD_T - PAD_B);

    const line = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p[1]).toFixed(1)}`).join("");
    const color = change >= 0 ? "var(--green)" : "var(--red)";
    const ns = "http://www.w3.org/2000/svg";

    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("preserveAspectRatio", "none");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", `Price chart, ${pct(change)}`);
    svg.innerHTML = `
        <defs><linearGradient id="fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stop-color="${color}" stop-opacity="0.25"/>
            <stop offset="1" stop-color="${color}" stop-opacity="0"/>
        </linearGradient></defs>
        <path d="${line}L${W},${H}L0,${H}Z" fill="url(#fill)"/>
        <path d="${line}" fill="none" stroke="${color}" stroke-width="2" vector-effect="non-scaling-stroke"/>
        <line id="cursor" y1="0" y2="${H}" stroke="var(--muted)" stroke-dasharray="3 3" vector-effect="non-scaling-stroke" visibility="hidden"/>`;

    const tip = el("div", { class: "tip", hidden: "" });
    box.replaceChildren(svg, tip);

    const cursor = svg.querySelector("#cursor");
    const longRange = state.chartDays > 1;

    svg.addEventListener("pointermove", (event) => {
        const rect = svg.getBoundingClientRect();
        const ratio = Math.min(Math.max((event.clientX - rect.left) / rect.width, 0), 1);
        const i = Math.round(ratio * (points.length - 1));
        const [ts, price] = points[i];
        cursor.setAttribute("x1", x(i));
        cursor.setAttribute("x2", x(i));
        cursor.setAttribute("visibility", "visible");
        const date = new Date(ts);
        tip.replaceChildren(
            el("b", {}, usd(price)),
            longRange ? date.toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "numeric" })
                : date.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" }),
        );
        tip.hidden = false;
        const px = (i / (points.length - 1)) * rect.width;
        tip.style.left = `${Math.min(Math.max(px, 60), rect.width - 60)}px`;
    });
    svg.addEventListener("pointerleave", () => {
        cursor.setAttribute("visibility", "hidden");
        tip.hidden = true;
    });
}

// ---------- Actions ----------

async function refresh(force = false) {
    const button = $("refresh");
    button.disabled = true;
    const q = force ? "?refresh=1" : "";

    try {
        const [market, summary] = await Promise.allSettled([
            api(`/api/market${q}`),
            api(`/api/portfolio${q}`),
        ]);
        if (market.status === "fulfilled") renderMarket(market.value);
        else renderMarket({});
        if (summary.status === "fulfilled") renderSummary(summary.value);
        else toast(summary.reason.message, true);

        $("updated").textContent = `Updated ${new Date().toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}`;
    } finally {
        button.disabled = false;
    }
    if (force) loadChart();
}

async function reloadSummary() {
    renderSummary(await api("/api/portfolio"));
}

async function removeHolding(assetId, symbol) {
    try {
        await api(`/api/holdings/${assetId}`, { method: "DELETE" });
        await reloadSummary();
        toast(`Removed manual ${symbol}.`);
    } catch (error) {
        toast(error.message, true);
    }
}

async function removeWallet(wallet) {
    if (!confirm(`Stop tracking "${wallet.label}"?`)) return;
    try {
        await api(`/api/wallets/${wallet.id}`, { method: "DELETE" });
        await reloadSummary();
        toast("Wallet removed.");
    } catch (error) {
        toast(error.message, true);
    }
}

$("holding-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const submit = form.querySelector("button");
    submit.disabled = true;
    try {
        await api(`/api/holdings/${form.asset.value}`, {
            method: "PUT",
            body: JSON.stringify({ amount: form.amount.value }),
        });
        form.amount.value = "";
        await reloadSummary();
        toast("Holding saved.");
    } catch (error) {
        toast(error.message, true);
    } finally {
        submit.disabled = false;
    }
});

$("wallet-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const submit = form.querySelector('button[type="submit"]');
    submit.disabled = true;
    submit.textContent = "Checking…";
    try {
        await api("/api/wallets", {
            method: "POST",
            body: JSON.stringify({
                chain: form.chain.value,
                address: form.address.value,
                label: form.label.value,
            }),
        });
        form.address.value = "";
        form.label.value = "";
        await reloadSummary();
        toast("Wallet added.");
    } catch (error) {
        toast(error.message, true);
    } finally {
        submit.disabled = false;
        submit.textContent = "Track";
    }
});

// Prefill the amount when picking an asset you already hold.
document.querySelector('#holding-form select').addEventListener("change", (event) => {
    const row = state.summary?.assets.find((a) => a.asset_id === event.target.value);
    $("holding-form").amount.value = row && row.manual_amount ? row.manual_amount : "";
});

$("ranges").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-days]");
    if (!button) return;
    state.chartDays = Number(button.dataset.days);
    document.querySelectorAll("#ranges button").forEach((b) => b.classList.toggle("active", b === button));
    loadChart();
});

document.querySelectorAll(".card[data-asset]").forEach((card) =>
    card.addEventListener("click", () => selectChartAsset(card.dataset.asset)));

$("refresh").addEventListener("click", () => refresh(true));

// Auto-refresh every 2 minutes while the tab is open.
setInterval(() => { if (!document.hidden) refresh(); }, 120000);

selectChartAsset(state.chartAsset);
refresh();
