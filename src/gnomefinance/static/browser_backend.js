// GNOMEfinance browser backend.
//
// GitHub Pages can only host static files, so there is no Python server.
// This file answers the same /api/... requests that web_app.py does, but
// right here in the browser: prices come straight from CoinGecko, wallet
// balances straight from public blockchain APIs, and your holdings are
// saved in this browser's localStorage. It mirrors service.py and chains.py.

(function () {
    const ASSETS = window.GNOME_ASSETS;
    const STORAGE_KEY = "gnomefinance";
    const QUOTES_KEY = "gnomefinance:quotes";
    const HISTORY_RANGES = [1, 7, 30, 90, 365];
    const MAX_LABEL_LENGTH = 40;

    const ENDPOINTS = {
        coingecko: "https://api.coingecko.com/api/v3",
        bitcoin: "https://mempool.space/api",
        ethereum: "https://ethereum-rpc.publicnode.com",
        solana: "https://solana-rpc.publicnode.com",
    };

    class HttpError extends Error {
        constructor(message, status) {
            super(message);
            this.status = status;
        }
    }
    const invalid = (message) => new HttpError(message, 400);

    // ---------- Small helpers ----------

    const cache = new Map();

    function cached(key, ttlSeconds) {
        const item = cache.get(key);
        return item && Date.now() - item.at < ttlSeconds * 1000 ? item.value : undefined;
    }

    function remember(key, value) {
        cache.set(key, { value, at: Date.now() });
        return value;
    }

    function readStore(key, fallback) {
        try {
            const raw = localStorage.getItem(key);
            return raw ? JSON.parse(raw) : fallback;
        } catch {
            return fallback;
        }
    }

    function writeStore(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch {
            // Private mode or storage disabled: the page still works, it just forgets.
        }
    }

    async function getJSON(url) {
        let response;
        try {
            response = await fetch(url);
        } catch {
            throw new HttpError(`Could not connect to ${new URL(url).host}.`, 502);
        }
        if (response.status === 429) throw new HttpError("Rate limited by the API. Try again in a minute.", 502);
        if (!response.ok) throw new HttpError(`API returned HTTP ${response.status}.`, 502);
        return response.json();
    }

    async function rpc(url, method, params) {
        let response;
        try {
            response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
            });
        } catch {
            throw new HttpError(`Could not connect to ${new URL(url).host}.`, 502);
        }
        if (!response.ok) throw new HttpError(`RPC returned HTTP ${response.status}.`, 502);
        const data = await response.json();
        if (data.error) throw new HttpError(`RPC error: ${data.error.message || data.error}`, 502);
        return data.result;
    }

    // ---------- Address validation (same rules as chains.py) ----------

    const B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

    function base58Decode(text) {
        let n = 0n;
        for (const ch of text) {
            const i = B58.indexOf(ch);
            if (i < 0) return null;
            n = n * 58n + BigInt(i);
        }
        const bytes = [];
        while (n > 0n) {
            bytes.unshift(Number(n & 255n));
            n >>= 8n;
        }
        const zeros = text.length - text.replace(/^1+/, "").length;
        return new Uint8Array([...new Array(zeros).fill(0), ...bytes]);
    }

    const BECH32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";

    function bech32Polymod(values) {
        const gen = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3];
        let chk = 1;
        for (const v of values) {
            const top = chk >>> 25;
            chk = (((chk & 0x1ffffff) << 5) ^ v) >>> 0;
            for (let i = 0; i < 5; i++) if ((top >>> i) & 1) chk = (chk ^ gen[i]) >>> 0;
        }
        return chk;
    }

    function validBech32(address, hrp = "bc") {
        if (address !== address.toLowerCase() && address !== address.toUpperCase()) return false;
        address = address.toLowerCase();
        if (address.length < 14 || address.length > 90) return false;
        const sep = address.lastIndexOf("1");
        if (address.slice(0, sep) !== hrp || sep + 7 > address.length) return false;
        const data = [];
        for (const ch of address.slice(sep + 1)) {
            const i = BECH32.indexOf(ch);
            if (i < 0) return false;
            data.push(i);
        }
        const expand = [...hrp].map((c) => c.charCodeAt(0) >> 5)
            .concat([0], [...hrp].map((c) => c.charCodeAt(0) & 31));
        const constant = bech32Polymod(expand.concat(data));
        return data[0] === 0 ? constant === 1 : data[0] <= 16 && constant === 0x2bc830a3;
    }

    async function validBase58Check(address) {
        const raw = base58Decode(address);
        if (!raw || raw.length !== 25 || ![0x00, 0x05].includes(raw[0])) return false;
        const once = await crypto.subtle.digest("SHA-256", raw.slice(0, 21));
        const twice = new Uint8Array(await crypto.subtle.digest("SHA-256", once));
        return twice.slice(0, 4).every((b, i) => b === raw[21 + i]);
    }

    const CHAINS = {
        bitcoin: {
            name: "Bitcoin",
            assetId: "bitcoin",
            explorer: (a) => `https://mempool.space/address/${a}`,
            validate: (a) => (a.toLowerCase().startsWith("bc1") ? validBech32(a) : validBase58Check(a)),
            async balance(address) {
                const data = await getJSON(`${ENDPOINTS.bitcoin}/address/${address}`);
                const c = data.chain_stats, m = data.mempool_stats;
                return (c.funded_txo_sum - c.spent_txo_sum + m.funded_txo_sum - m.spent_txo_sum) / 1e8;
            },
        },
        ethereum: {
            name: "Ethereum",
            assetId: "ethereum",
            explorer: (a) => `https://etherscan.io/address/${a}`,
            validate: (a) => /^0x[0-9a-fA-F]{40}$/.test(a),
            async balance(address) {
                const wei = BigInt(await rpc(ENDPOINTS.ethereum, "eth_getBalance", [address, "latest"]));
                return Number(wei / 10n ** 9n) / 1e9;
            },
        },
        solana: {
            name: "Solana",
            assetId: "solana",
            explorer: (a) => `https://solscan.io/account/${a}`,
            validate: (a) => {
                if (a.length < 32 || a.length > 44) return false;
                const raw = base58Decode(a);
                return raw !== null && raw.length === 32;
            },
            async balance(address) {
                const result = await rpc(ENDPOINTS.solana, "getBalance", [address]);
                return result.value / 1e9;
            },
        },
    };

    function getChain(chainId) {
        const chain = CHAINS[chainId];
        if (!chain) throw invalid(`Unsupported chain: ${chainId}`);
        return chain;
    }

    async function cleanAddress(chain, address) {
        address = String(address || "").trim();
        if (!(await chain.validate(address))) throw invalid(`That is not a valid ${chain.name} address.`);
        return address;
    }

    // ---------- Portfolio storage ----------

    function load() {
        const data = readStore(STORAGE_KEY, {});
        return { holdings: data.holdings || {}, wallets: data.wallets || [] };
    }

    function save(data) {
        writeStore(STORAGE_KEY, data);
    }

    function parseAmount(value) {
        const amount = Number(value);
        if (value === null || value === "" || !Number.isFinite(amount)) throw invalid(`Not a number: ${value}`);
        if (amount < 0) throw invalid("Amount cannot be negative.");
        return amount;
    }

    // ---------- Market data ----------

    async function quotes(force) {
        if (!force) {
            const hit = cached("quotes", 60);
            if (hit) return hit;
        }

        const byGecko = {};
        for (const [id, info] of Object.entries(ASSETS)) byGecko[info.coingecko_id] = id;

        try {
            const ids = Object.keys(byGecko).join(",");
            const data = await getJSON(
                `${ENDPOINTS.coingecko}/coins/markets?vs_currency=usd&ids=${ids}&price_change_percentage=24h`);
            const result = {};
            for (const coin of data) {
                const id = byGecko[coin.id];
                if (!id || coin.current_price == null) continue;
                result[id] = {
                    price: coin.current_price,
                    change_24h: coin.price_change_percentage_24h || 0,
                    market_cap: coin.market_cap || 0,
                    volume_24h: coin.total_volume || 0,
                    updated: Date.now() / 1000,
                    stale: false,
                };
            }
            writeStore(QUOTES_KEY, result);
            return remember("quotes", result);
        } catch (error) {
            const last = cache.get("quotes")?.value || readStore(QUOTES_KEY, null);
            if (!last) throw error;
            return Object.fromEntries(Object.entries(last).map(([id, q]) => [id, { ...q, stale: true }]));
        }
    }

    async function history(assetId, days) {
        if (!ASSETS[assetId]) throw invalid(`Unknown asset: ${assetId}`);
        if (!HISTORY_RANGES.includes(days)) throw invalid(`days must be one of ${HISTORY_RANGES.join(", ")}`);

        const key = `history:${assetId}:${days}`;
        const hit = cached(key, days === 1 ? 60 : days <= 7 ? 300 : 1800);
        if (hit) return hit;

        const data = await getJSON(
            `${ENDPOINTS.coingecko}/coins/${ASSETS[assetId].coingecko_id}/market_chart?vs_currency=usd&days=${days}`);
        return remember(key, (data.prices || []).filter((p) => p[1] != null));
    }

    // ---------- Wallets ----------

    async function walletBalances(force) {
        return Promise.all(load().wallets.map(async (wallet) => {
            const chain = CHAINS[wallet.chain];
            const key = `balance:${wallet.chain}:${wallet.address}`;
            let balance = force ? undefined : cached(key, 120);
            let error = null;

            if (balance === undefined) {
                try {
                    balance = remember(key, await chain.balance(wallet.address));
                } catch (exc) {
                    balance = cache.get(key)?.value ?? null;
                    error = exc.message;
                }
            }

            return {
                ...wallet,
                asset_id: chain.assetId,
                symbol: ASSETS[chain.assetId].symbol,
                balance,
                error,
                explorer_url: chain.explorer(wallet.address),
            };
        }));
    }

    // ---------- Summary (same math as service.py) ----------

    async function summary(force) {
        const errors = [];
        let q = {};
        try {
            q = await quotes(force);
        } catch (error) {
            errors.push(`Prices unavailable: ${error.message}`);
        }

        const wallets = await walletBalances(force);
        const onChain = {};
        for (const w of wallets) {
            if (w.error) errors.push(`${w.label}: ${w.error}`);
            if (w.balance != null) onChain[w.asset_id] = (onChain[w.asset_id] || 0) + w.balance;
        }

        const manual = load().holdings;
        const rows = [];

        for (const [id, info] of Object.entries(ASSETS)) {
            const manualAmount = manual[id] || 0;
            const walletAmount = onChain[id] || 0;
            const amount = manualAmount + walletAmount;
            if (amount <= 0 && !(id in manual)) continue;

            const quote = q[id];
            const price = quote ? quote.price : null;
            const change = quote ? quote.change_24h : 0;
            const value = price !== null ? amount * price : null;
            const valueChange = value !== null && change > -100 ? value - value / (1 + change / 100) : 0;

            rows.push({
                asset_id: id,
                name: info.name,
                symbol: info.symbol,
                icon: info.icon,
                amount,
                manual_amount: manualAmount,
                wallet_amount: walletAmount,
                wallet_count: wallets.filter((w) => w.asset_id === id).length,
                price,
                change_24h: change,
                value,
                value_change_24h: valueChange,
            });
        }

        const total = rows.reduce((sum, r) => sum + (r.value || 0), 0);
        const totalChange = rows.reduce((sum, r) => sum + r.value_change_24h, 0);
        const previous = total - totalChange;
        for (const r of rows) r.allocation = total > 0 ? ((r.value || 0) / total) * 100 : 0;
        rows.sort((a, b) => (b.value || 0) - (a.value || 0));

        return {
            assets: rows,
            wallets,
            total_value: total,
            change_24h: totalChange,
            change_24h_pct: previous > 0 ? (totalChange / previous) * 100 : 0,
            prices_stale: Object.values(q).some((x) => x.stale),
            errors,
        };
    }

    // ---------- Router: the same URLs as web_app.py ----------

    async function handle(path, options) {
        const url = new URL(path, location.href);
        const method = (options.method || "GET").toUpperCase();
        const force = ["1", "true", "yes"].includes(url.searchParams.get("refresh"));
        const body = options.body ? JSON.parse(options.body) : {};
        const parts = url.pathname.split("/").filter(Boolean).slice(-3);
        const route = url.pathname.slice(url.pathname.indexOf("/api/"));
        let m;

        if (route === "/api/market") return quotes(force);
        if (route === "/api/portfolio") return summary(force);
        if (route === "/api/wallets" && method === "GET") return walletBalances(force);

        if ((m = route.match(/^\/api\/history\/([\w-]+)$/))) {
            return history(m[1], Number(url.searchParams.get("days") || 7));
        }

        if ((m = route.match(/^\/api\/holdings\/([\w-]+)$/))) {
            const assetId = m[1];
            if (!ASSETS[assetId]) throw invalid(`Unknown asset: ${assetId}`);
            const data = load();
            if (method === "PUT") {
                const amount = parseAmount(body.amount);
                if (amount === 0) delete data.holdings[assetId];
                else data.holdings[assetId] = amount;
            } else if (method === "DELETE") {
                delete data.holdings[assetId];
            }
            save(data);
            return data.holdings;
        }

        if (route === "/api/wallets" && method === "POST") {
            const chain = getChain(body.chain);
            const address = await cleanAddress(chain, body.address);
            const data = load();
            if (data.wallets.some((w) => w.chain === body.chain && w.address === address)) {
                throw invalid("You are already tracking that wallet.");
            }
            const wallet = {
                id: crypto.getRandomValues(new Uint32Array(1))[0].toString(16).padStart(8, "0"),
                chain: body.chain,
                address,
                label: String(body.label || "").trim().slice(0, MAX_LABEL_LENGTH) || `${chain.name} wallet`,
            };
            data.wallets.push(wallet);
            save(data);
            return wallet;
        }

        if ((m = route.match(/^\/api\/wallets\/(\w+)$/)) && method === "DELETE") {
            const data = load();
            const before = data.wallets.length;
            data.wallets = data.wallets.filter((w) => w.id !== m[1]);
            if (data.wallets.length === before) throw invalid(`No wallet with id ${m[1]}`);
            save(data);
            return null;
        }

        throw new HttpError(`Not found: ${parts.join("/")}`, 404);
    }

    window.GnomeBackend = { request: handle };
})();
