// GNOMEfinance Solana DApp: connect a wallet, see tokens, send, and swap.
//
// How it stays safe:
// - We never see a private key. Your wallet (Phantom, Solflare, Backpack)
//   signs each transaction after showing you what it does.
// - Every transaction is shown in our own confirm dialog first, then in
//   your wallet's approval window.
// - Swap transactions built by Jupiter are checked to make sure *you* are
//   the fee payer before we ask your wallet to sign them.

(function () {
    const web3 = window.solanaWeb3;
    if (!web3) return;

    const { PublicKey, TransactionInstruction, TransactionMessage, VersionedTransaction } = web3;

    const SOL_MINT = "So11111111111111111111111111111111111111112";
    const TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA";
    const TOKEN_2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb";
    const ATA_PROGRAM = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL";
    const SYSTEM_PROGRAM = "11111111111111111111111111111111";
    const COMPUTE_BUDGET_PROGRAM = "ComputeBudget111111111111111111111111111111";
    const JUPITER = "https://lite-api.jup.ag";

    const NETWORKS = {
        mainnet: { rpc: "https://solana-rpc.publicnode.com", explorer: "" },
        devnet: { rpc: "https://api.devnet.solana.com", explorer: "?cluster=devnet" },
    };

    // Tokens offered in the swap "receive" list even if you don't hold them.
    const POPULAR = [
        [SOL_MINT, "SOL"],
        ["EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "USDC"],
        ["Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", "USDT"],
        ["JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", "JUP"],
        ["DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "BONK"],
        ["jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL", "JTO"],
        ["EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "WIF"],
        ["HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3", "PYTH"],
        ["4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", "RAY"],
    ];

    const RESERVE_LAMPORTS = 2_000_000n;   // keep 0.002 SOL for fees/rent
    const PRIORITY_MICROLAMPORTS = 50_000; // small tip so sends land when busy
    const MAX_PRICE_IMPACT = 20;           // refuse swaps worse than this (%)

    const state = {
        provider: null,
        owner: null,          // PublicKey
        network: readSetting("network", "mainnet"),
        tokens: [],           // [{mint, symbol, name, icon, decimals, raw (BigInt), ui, usd, price, program}]
        quote: null,
        quoteSeq: 0,
    };

    // ---------- Helpers ----------

    const $ = (id) => document.getElementById(id);

    function readSetting(key, fallback) {
        try { return localStorage.getItem(`gnome:${key}`) ?? fallback; } catch { return fallback; }
    }

    function writeSetting(key, value) {
        try {
            if (value === null) localStorage.removeItem(`gnome:${key}`);
            else localStorage.setItem(`gnome:${key}`, value);
        } catch { /* storage disabled */ }
    }

    function short(address) {
        return `${address.slice(0, 4)}…${address.slice(-4)}`;
    }

    function rpcUrl() {
        return NETWORKS[state.network].rpc;
    }

    // A tiny JSON-RPC client. (web3.js's Connection needs Node's Buffer,
    // which browsers don't have, so we talk to the RPC node directly.)
    let rpcId = 0;
    async function rpc(method, params = []) {
        let response;
        try {
            response = await fetch(rpcUrl(), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ jsonrpc: "2.0", id: ++rpcId, method, params }),
            });
        } catch {
            throw new Error(`Could not reach the Solana network (${new URL(rpcUrl()).host}).`);
        }
        if (response.status === 429) throw new Error("The Solana RPC is busy. Try again in a moment.");
        const data = await response.json().catch(() => ({}));
        if (data.error) throw new Error(data.error.message || JSON.stringify(data.error));
        if (!response.ok) throw new Error(`Solana RPC returned HTTP ${response.status}.`);
        return data.result;
    }

    function toBase64(bytes) {
        let binary = "";
        for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
        return btoa(binary);
    }

    const solana = {
        balance: async (owner) => (await rpc("getBalance", [owner.toBase58(), { commitment: "confirmed" }])).value,
        accountOwner: async (address) => {
            const result = await rpc("getAccountInfo", [address.toBase58(), { encoding: "base64", dataSlice: { offset: 0, length: 0 } }]);
            return result.value?.owner ?? null;
        },
        tokenAccounts: async (owner, program) => (await rpc("getTokenAccountsByOwner",
            [owner.toBase58(), { programId: program }, { encoding: "jsonParsed", commitment: "confirmed" }])).value,
        latestBlockhash: async () => (await rpc("getLatestBlockhash", [{ commitment: "confirmed" }])).value,
        blockHeight: () => rpc("getBlockHeight", [{ commitment: "confirmed" }]),
        send: (raw, skipPreflight) => rpc("sendTransaction",
            [toBase64(raw), { encoding: "base64", skipPreflight, preflightCommitment: "confirmed", maxRetries: 0 }]),
        status: async (signature) => (await rpc("getSignatureStatuses", [[signature]])).value[0],
    };

    function explorerTx(signature) {
        return `https://solscan.io/tx/${signature}${NETWORKS[state.network].explorer}`;
    }

    // Decimal string -> integer base units, with no floating point rounding.
    function toBaseUnits(text, decimals) {
        text = String(text).trim();
        if (!/^\d*\.?\d*$/.test(text) || text === "" || text === ".") throw new Error("Enter a valid amount.");
        const [whole, frac = ""] = text.split(".");
        if (frac.length > decimals) throw new Error(`This token only has ${decimals} decimal places.`);
        const units = BigInt(whole || "0") * 10n ** BigInt(decimals) + BigInt(frac.padEnd(decimals, "0") || "0");
        if (units <= 0n) throw new Error("Amount must be more than zero.");
        return units;
    }

    function fromBaseUnits(units, decimals) {
        units = BigInt(units);
        const base = 10n ** BigInt(decimals);
        const frac = (units % base).toString().padStart(decimals, "0").replace(/0+$/, "");
        return frac ? `${units / base}.${frac}` : `${units / base}`;
    }

    // Little-endian integers, the byte order Solana programs expect.
    function u64(value) {
        const bytes = new Uint8Array(8);
        new DataView(bytes.buffer).setBigUint64(0, BigInt(value), true);
        return bytes;
    }

    function u32(value) {
        const bytes = new Uint8Array(4);
        new DataView(bytes.buffer).setUint32(0, value, true);
        return bytes;
    }

    // Instructions are just bytes. Building them by hand keeps this file
    // free of Node-only code and shows exactly what gets signed.
    const instruction = {
        computeUnitLimit: (units) => new TransactionInstruction({
            programId: new PublicKey(COMPUTE_BUDGET_PROGRAM), keys: [],
            data: Uint8Array.from([2, ...u32(units)]),
        }),
        computeUnitPrice: (microLamports) => new TransactionInstruction({
            programId: new PublicKey(COMPUTE_BUDGET_PROGRAM), keys: [],
            data: Uint8Array.from([3, ...u64(microLamports)]),
        }),
        // System program "Transfer" (index 2): move lamports between wallets.
        transferSol: (from, to, lamports) => new TransactionInstruction({
            programId: new PublicKey(SYSTEM_PROGRAM),
            keys: [
                { pubkey: from, isSigner: true, isWritable: true },
                { pubkey: to, isSigner: false, isWritable: true },
            ],
            data: Uint8Array.from([...u32(2), ...u64(lamports)]),
        }),
    };

    function parseAddress(text) {
        try {
            const key = new PublicKey(String(text).trim());
            return key;
        } catch {
            throw new Error("That is not a valid Solana address.");
        }
    }

    async function getJSON(url, options) {
        let response;
        try {
            response = await fetch(url, options);
        } catch {
            throw new Error(`Could not reach ${new URL(url).host}.`);
        }
        if (response.status === 429) throw new Error("Jupiter is busy (rate limited). Wait a few seconds and try again.");
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || data.message || `HTTP ${response.status}`);
        return data;
    }

    function tokenByMint(mint) {
        return state.tokens.find((t) => t.mint === mint);
    }

    // ---------- Wallet ----------

    function findProvider() {
        const candidates = [
            window.phantom?.solana,
            window.solflare,
            window.backpack,
            window.solana,
        ];
        return candidates.find((p) => p && typeof p.connect === "function" && typeof p.signTransaction === "function");
    }

    function walletName(provider) {
        if (provider?.isPhantom) return "Phantom";
        if (provider?.isSolflare) return "Solflare";
        if (provider?.isBackpack) return "Backpack";
        return "Wallet";
    }

    async function connect(silent = false) {
        const provider = findProvider();
        if (!provider) {
            if (!silent) {
                toast("No Solana wallet found. Install Phantom, Solflare or Backpack, then reload.", true);
                window.open("https://phantom.com/download", "_blank", "noopener");
            }
            return;
        }

        try {
            const result = await provider.connect(silent ? { onlyIfTrusted: true } : undefined);
            const key = result?.publicKey || provider.publicKey;
            if (!key) return;
            state.provider = provider;
            state.owner = new PublicKey(key.toString());
            writeSetting("autoconnect", "1");
            bindProviderEvents(provider);
            renderConnection();
            await loadTokens();
        } catch (error) {
            if (!silent) toast(error.message || "Wallet connection was cancelled.", true);
        }
    }

    async function disconnect() {
        try { await state.provider?.disconnect(); } catch { /* already gone */ }
        state.provider = null;
        state.owner = null;
        state.tokens = [];
        writeSetting("autoconnect", null);
        renderConnection();
    }

    let eventsBound = false;
    function bindProviderEvents(provider) {
        if (eventsBound || typeof provider.on !== "function") return;
        eventsBound = true;
        provider.on("accountChanged", (key) => {
            if (!key) return disconnect();
            state.owner = new PublicKey(key.toString());
            renderConnection();
            loadTokens();
        });
        provider.on("disconnect", () => {
            state.provider = null;
            state.owner = null;
            renderConnection();
        });
    }

    function renderConnection() {
        const connected = Boolean(state.owner);
        $("dapp-who").classList.toggle("on", connected);
        $("dapp-status").textContent = connected
            ? `${walletName(state.provider)} · ${short(state.owner.toBase58())}`
            : "Not connected";
        $("dapp-status").title = connected ? state.owner.toBase58() : "";
        $("dapp-connect").textContent = connected ? "Disconnect" : "Connect wallet";
        $("dapp-connect").classList.toggle("primary", !connected);
        $("dapp-body").hidden = !connected;
        $("dapp-devnet-note").hidden = state.network !== "devnet";
        $("swap-devnet").hidden = state.network !== "devnet";
        $("swap-form").hidden = state.network === "devnet";
    }

    // ---------- Token balances ----------

    async function loadTokens() {
        if (!state.owner) return;
        const list = $("dapp-tokens");
        list.replaceChildren(el("li", { class: "empty" }, "Loading tokens…"));

        try {
            state.tokens = state.network === "mainnet"
                ? await loadMainnetTokens(state.owner.toBase58())
                : await loadRpcTokens(state.owner);
        } catch (error) {
            list.replaceChildren(el("li", { class: "empty" }, `Could not load tokens: ${error.message}`));
            return;
        }
        renderTokens();
        fillTokenSelects();
    }

    // Jupiter's holdings API lists every token in one request.
    async function loadMainnetTokens(owner) {
        const data = await getJSON(`${JUPITER}/ultra/v1/holdings/${owner}`);
        const tokens = [{
            mint: SOL_MINT, symbol: "SOL", name: "Solana", decimals: 9,
            raw: BigInt(data.amount || 0), program: null,
        }];

        for (const [mint, accounts] of Object.entries(data.tokens || {})) {
            if (mint === SOL_MINT) continue; // wrapped SOL; Jupiter unwraps for us
            const raw = accounts.reduce((sum, a) => sum + BigInt(a.amount || 0), 0n);
            if (raw === 0n) continue;
            tokens.push({
                mint, symbol: short(mint), name: "", decimals: accounts[0].decimals,
                raw, program: accounts[0].programId,
            });
        }

        // Names, icons and prices, 100 mints per request.
        const popular = new Set(POPULAR.map(([mint]) => mint));
        const mints = tokens.map((t) => t.mint).sort((a, b) => popular.has(b) - popular.has(a));
        for (let i = 0; i < mints.length && i < 300; i += 100) {
            try {
                const info = await getJSON(`${JUPITER}/tokens/v2/search?query=${mints.slice(i, i + 100).join(",")}`);
                for (const meta of info) {
                    const token = tokens.find((t) => t.mint === meta.id);
                    if (!token) continue;
                    token.symbol = meta.symbol || token.symbol;
                    token.name = meta.name || "";
                    token.icon = /^https:\/\//.test(meta.icon || "") ? meta.icon : null;
                    token.price = meta.usdPrice ?? null;
                    token.verified = Boolean(meta.isVerified);
                }
            } catch { /* names are nice-to-have */ }
        }

        return finishTokens(tokens);
    }

    // Devnet (or anything without Jupiter): ask the RPC node directly.
    async function loadRpcTokens(owner) {
        const tokens = [{
            mint: SOL_MINT, symbol: "SOL", name: "Solana", decimals: 9,
            raw: BigInt(await solana.balance(owner)), program: null, price: null,
        }];

        for (const program of [TOKEN_PROGRAM, TOKEN_2022_PROGRAM]) {
            for (const { account } of await solana.tokenAccounts(owner, program)) {
                const info = account.data.parsed.info;
                const raw = BigInt(info.tokenAmount.amount);
                if (raw === 0n) continue;
                const existing = tokens.find((t) => t.mint === info.mint);
                if (existing) existing.raw += raw;
                else tokens.push({
                    mint: info.mint, symbol: short(info.mint), name: "", decimals: info.tokenAmount.decimals,
                    raw, program, price: null,
                });
            }
        }
        return finishTokens(tokens);
    }

    function finishTokens(tokens) {
        for (const t of tokens) {
            t.ui = Number(fromBaseUnits(t.raw, t.decimals));
            t.usd = t.price != null ? t.ui * t.price : null;
            if (t.mint === SOL_MINT) t.verified = true;
        }
        return tokens.sort((a, b) => (b.usd ?? -1) - (a.usd ?? -1) || b.ui - a.ui);
    }

    function renderTokens() {
        const list = $("dapp-tokens");
        list.replaceChildren();
        const total = state.tokens.reduce((sum, t) => sum + (t.usd || 0), 0);
        $("dapp-total").textContent = state.network === "mainnet" ? usd(total) : "Devnet balances";

        for (const t of state.tokens.slice(0, 100)) {
            const icon = t.icon
                ? el("img", { src: t.icon, alt: "", loading: "lazy", referrerpolicy: "no-referrer" })
                : el("span", { class: "token-icon" }, t.symbol.slice(0, 1));
            list.append(el("li", {},
                icon,
                el("div", { class: "token-name" },
                    el("b", {}, t.symbol, t.verified ? "" : el("span", { class: "unverified", title: "Not on Jupiter's verified list" }, " ⚠")),
                    el("small", {}, t.name || t.mint)),
                el("div", { class: "token-amt" },
                    amount(t.ui),
                    el("small", {}, t.usd != null ? usd(t.usd) : "")),
            ));
        }
    }

    function tokenOption(t, extra = "") {
        return el("option", { value: t.mint }, `${t.symbol}${extra}`);
    }

    function fillTokenSelects() {
        const keep = (select) => select.value;
        const send = $("send-token"), from = $("swap-from"), to = $("swap-to");
        const [sendWas, fromWas, toWas] = [keep(send), keep(from), keep(to)];

        send.replaceChildren(...state.tokens.map((t) => tokenOption(t, ` · ${amount(t.ui)}`)));
        from.replaceChildren(...state.tokens.map((t) => tokenOption(t)));

        const seen = new Set();
        const targets = [];
        for (const [mint, symbol] of POPULAR) {
            seen.add(mint);
            targets.push(el("option", { value: mint }, symbol));
        }
        for (const t of state.tokens) if (!seen.has(t.mint)) targets.push(tokenOption(t));
        to.replaceChildren(...targets);

        if (sendWas) send.value = sendWas;
        from.value = fromWas || SOL_MINT;
        to.value = toWas || "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";
        if (to.value === from.value) to.value = from.value === SOL_MINT ? POPULAR[1][0] : SOL_MINT;
        updateSendHint();
    }

    // ---------- Sending transactions ----------

    // Signs with the wallet, broadcasts, and waits for confirmation.
    async function signSendConfirm(tx, lastValidBlockHeight, onStatus) {
        onStatus("Waiting for your approval in the wallet…");
        const signed = await state.provider.signTransaction(tx);
        const raw = signed.serialize();

        onStatus("Sending to the network…");
        const signature = await solana.send(raw, false);

        onStatus("Confirming…");
        const started = Date.now();
        while (Date.now() - started < 90_000) {
            const status = await solana.status(signature);
            if (status?.err) throw new Error(`Transaction failed on-chain: ${JSON.stringify(status.err)}`);
            if (status && ["confirmed", "finalized"].includes(status.confirmationStatus)) return signature;
            if (lastValidBlockHeight && (await solana.blockHeight()) > lastValidBlockHeight) {
                throw new Error("Transaction expired before it landed. Nothing was sent; please try again.");
            }
            // Re-broadcast while waiting; Solana drops some transactions when busy.
            solana.send(raw, true).catch(() => {});
            await new Promise((resolve) => setTimeout(resolve, 2000));
        }
        throw new Error(`Still not confirmed after 90s. Check Solscan: ${signature}`);
    }

    function ataAddress(owner, mint, program) {
        return PublicKey.findProgramAddressSync(
            [owner.toBytes(), new PublicKey(program).toBytes(), mint.toBytes()],
            new PublicKey(ATA_PROGRAM),
        )[0];
    }

    async function buildSend(token, recipient, units) {
        const owner = state.owner;
        const instructions = [
            instruction.computeUnitLimit(60_000),
            instruction.computeUnitPrice(PRIORITY_MICROLAMPORTS),
        ];

        // Refuse to send to a token account by mistake: funds there are usually lost.
        const ownerProgram = await solana.accountOwner(recipient);
        if (ownerProgram === TOKEN_PROGRAM || ownerProgram === TOKEN_2022_PROGRAM) {
            throw new Error("That address is a token account, not a wallet. Ask for their main wallet address.");
        }

        if (token.mint === SOL_MINT) {
            instructions.push(instruction.transferSol(owner, recipient, units));
        } else {
            const mint = new PublicKey(token.mint);
            const program = new PublicKey(token.program);
            const source = ataAddress(owner, mint, token.program);
            const dest = ataAddress(recipient, mint, token.program);

            // Create the recipient's token account if they don't have one (no-op if they do).
            instructions.push(new TransactionInstruction({
                programId: new PublicKey(ATA_PROGRAM),
                keys: [
                    { pubkey: owner, isSigner: true, isWritable: true },
                    { pubkey: dest, isSigner: false, isWritable: true },
                    { pubkey: recipient, isSigner: false, isWritable: false },
                    { pubkey: mint, isSigner: false, isWritable: false },
                    { pubkey: new PublicKey(SYSTEM_PROGRAM), isSigner: false, isWritable: false },
                    { pubkey: program, isSigner: false, isWritable: false },
                ],
                data: Uint8Array.of(1), // CreateIdempotent
            }));

            // TransferChecked: [12, amount u64, decimals u8]
            instructions.push(new TransactionInstruction({
                programId: program,
                keys: [
                    { pubkey: source, isSigner: false, isWritable: true },
                    { pubkey: mint, isSigner: false, isWritable: false },
                    { pubkey: dest, isSigner: false, isWritable: true },
                    { pubkey: owner, isSigner: true, isWritable: false },
                ],
                data: Uint8Array.from([12, ...u64(units), token.decimals]),
            }));
        }

        const { blockhash, lastValidBlockHeight } = await solana.latestBlockhash();
        const message = new TransactionMessage({
            payerKey: owner,
            recentBlockhash: blockhash,
            instructions,
        }).compileToV0Message();

        return { tx: new VersionedTransaction(message), lastValidBlockHeight };
    }

    function maxSendable(token) {
        if (token.mint !== SOL_MINT) return token.raw;
        const max = token.raw - RESERVE_LAMPORTS;
        return max > 0n ? max : 0n;
    }

    function updateSendHint() {
        const token = tokenByMint($("send-token").value);
        $("send-hint").textContent = token
            ? `Available: ${fromBaseUnits(maxSendable(token), token.decimals)} ${token.symbol}` +
              (token.mint === SOL_MINT ? " (0.002 SOL kept for fees)" : "")
            : "";
    }

    async function reviewSend(event) {
        event.preventDefault();
        const form = event.target;
        let token, recipient, units;

        try {
            token = tokenByMint(form.token.value);
            if (!token) throw new Error("Pick a token to send.");
            recipient = parseAddress(form.to.value);
            if (recipient.equals(state.owner)) throw new Error("That's your own address.");
            units = toBaseUnits(form.amount.value, token.decimals);
            if (units > maxSendable(token)) throw new Error("That's more than you can send.");
        } catch (error) {
            return toast(error.message, true);
        }

        const amountText = `${fromBaseUnits(units, token.decimals)} ${token.symbol}`;
        const value = token.price != null ? ` (${usd(Number(fromBaseUnits(units, token.decimals)) * token.price)})` : "";

        await confirmAndRun({
            title: "Send",
            details: [
                ["Sending", amountText + value],
                ["To", recipient.toBase58()],
                ["Network", state.network === "mainnet" ? "Solana mainnet (real money)" : "Solana devnet (test)"],
                ["Network fee", "≈ 0.00001 SOL"],
            ],
            warning: token.mint !== SOL_MINT
                ? "If the recipient has never held this token, about 0.002 SOL extra is used to open their token account."
                : null,
            run: async (onStatus) => {
                onStatus("Preparing transaction…");
                const { tx, lastValidBlockHeight } = await buildSend(token, recipient, units);
                return signSendConfirm(tx, lastValidBlockHeight, onStatus);
            },
            done: () => { form.to.value = ""; form.amount.value = ""; },
        });
    }

    // ---------- Swaps (Jupiter) ----------

    let quoteTimer;
    function scheduleQuote() {
        clearTimeout(quoteTimer);
        state.quote = null;
        $("swap-submit").disabled = true;
        quoteTimer = setTimeout(getQuote, 600);
    }

    async function swapTarget() {
        const pasted = $("swap-mint").value.trim();
        if (!pasted) {
            const option = $("swap-to").selectedOptions[0];
            const held = tokenByMint($("swap-to").value);
            return { mint: $("swap-to").value, symbol: option?.textContent || held?.symbol, decimals: held?.decimals, verified: held?.verified };
        }
        parseAddress(pasted);
        const [meta] = await getJSON(`${JUPITER}/tokens/v2/search?query=${pasted}`);
        if (!meta || meta.id !== pasted) throw new Error("Jupiter doesn't know that token mint.");
        return { mint: meta.id, symbol: meta.symbol, decimals: meta.decimals, verified: meta.isVerified };
    }

    async function getQuote() {
        const box = $("swap-quote");
        const seq = ++state.quoteSeq;
        const from = tokenByMint($("swap-from").value);
        const text = $("swap-form").amount.value;

        if (!from || !text) {
            box.textContent = "Enter an amount to get a quote.";
            return;
        }

        try {
            const units = toBaseUnits(text, from.decimals);
            if (units > maxSendable(from)) throw new Error(`You only have ${fromBaseUnits(maxSendable(from), from.decimals)} ${from.symbol} available.`);
            const to = await swapTarget();
            if (to.mint === from.mint) throw new Error("Pick two different tokens.");

            box.textContent = "Finding the best route…";
            const slippage = $("swap-slippage").value;
            const quote = await getJSON(`${JUPITER}/swap/v1/quote?inputMint=${from.mint}&outputMint=${to.mint}` +
                `&amount=${units}&slippageBps=${slippage}&restrictIntermediateTokens=true`);
            if (seq !== state.quoteSeq) return; // a newer quote is on its way

            if (to.decimals == null) {
                const [meta] = await getJSON(`${JUPITER}/tokens/v2/search?query=${to.mint}`);
                to.decimals = meta.decimals;
                to.verified = meta.isVerified;
            }

            const impact = Number(quote.priceImpactPct || 0) * 100;
            state.quote = { quote, from, to, units, impact };

            const route = quote.routePlan.map((r) => r.swapInfo.label).filter(Boolean).join(" → ");
            box.replaceChildren(...[
                el("div", {}, "You receive ≈ ", el("b", {}, `${amount(Number(fromBaseUnits(quote.outAmount, to.decimals)))} ${to.symbol}`)),
                el("div", { class: "muted" }, `Minimum after ${slippage / 100}% slippage: ${amount(Number(fromBaseUnits(quote.otherAmountThreshold, to.decimals)))} ${to.symbol}`),
                el("div", { class: impact > 5 ? "down" : impact > 1 ? "warn-text" : "muted" }, `Price impact: ${impact.toFixed(3)}%`),
                route ? el("div", { class: "muted" }, `Route: ${route}`) : null,
                to.verified === false ? el("div", { class: "down" }, "⚠ This token isn't on Jupiter's verified list. Make sure it's the one you want.") : null,
            ].filter(Boolean));
            $("swap-submit").disabled = impact > MAX_PRICE_IMPACT;
            if (impact > MAX_PRICE_IMPACT) box.append(el("div", { class: "down" }, "Price impact is too high. Try a smaller amount."));
        } catch (error) {
            if (seq === state.quoteSeq) box.replaceChildren(el("span", { class: "down" }, error.message));
        }
    }

    async function reviewSwap(event) {
        event.preventDefault();
        const q = state.quote;
        if (!q) return;

        const pay = `${fromBaseUnits(q.units, q.from.decimals)} ${q.from.symbol}`;
        const get = `${amount(Number(fromBaseUnits(q.quote.outAmount, q.to.decimals)))} ${q.to.symbol}`;
        const min = `${amount(Number(fromBaseUnits(q.quote.otherAmountThreshold, q.to.decimals)))} ${q.to.symbol}`;

        await confirmAndRun({
            title: "Swap",
            details: [
                ["You pay", pay],
                ["You receive ≈", get],
                ["At least", min],
                ["Price impact", `${q.impact.toFixed(3)}%`],
                ["Network", "Solana mainnet (real money)"],
            ],
            warning: q.impact > 5 || q.to.verified === false
                ? "Double-check this one: " + [
                    q.impact > 5 ? "price impact is high" : null,
                    q.to.verified === false ? "the token you receive is unverified" : null,
                ].filter(Boolean).join(" and ") + "."
                : null,
            run: async (onStatus) => {
                onStatus("Building swap with Jupiter…");
                const data = await getJSON(`${JUPITER}/swap/v1/swap`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        quoteResponse: q.quote,
                        userPublicKey: state.owner.toBase58(),
                        dynamicComputeUnitLimit: true,
                        dynamicSlippage: false,
                        prioritizationFeeLamports: {
                            priorityLevelWithMaxLamports: { maxLamports: 1_000_000, priorityLevel: "high" },
                        },
                    }),
                });

                const bytes = Uint8Array.from(atob(data.swapTransaction), (c) => c.charCodeAt(0));
                const tx = VersionedTransaction.deserialize(bytes);

                // Safety: the transaction must be paid for and signed only by you.
                const payer = tx.message.staticAccountKeys[0];
                if (!payer.equals(state.owner) || tx.message.header.numRequiredSignatures !== 1) {
                    throw new Error("Jupiter returned an unexpected transaction. Nothing was signed.");
                }
                return signSendConfirm(tx, data.lastValidBlockHeight, onStatus);
            },
            done: () => {
                $("swap-form").amount.value = "";
                $("swap-quote").textContent = "Enter an amount to get a quote.";
                state.quote = null;
                $("swap-submit").disabled = true;
            },
        });
    }

    // ---------- Confirm dialog ----------

    function confirmAndRun({ title, details, warning, run, done }) {
        const dialog = $("confirm");
        const ok = $("confirm-ok");
        const cancel = $("confirm-cancel");
        const status = $("confirm-status");

        $("confirm-title").textContent = title;
        $("confirm-details").replaceChildren(...details.flatMap(([k, v]) => [el("dt", {}, k), el("dd", {}, v)]));
        $("confirm-warning").hidden = !warning;
        $("confirm-warning").textContent = warning || "";
        status.hidden = true;
        status.className = "confirm-status";
        ok.hidden = false;
        ok.disabled = false;
        ok.textContent = "Approve in wallet";
        cancel.textContent = "Cancel";
        cancel.disabled = false;

        return new Promise((resolve) => {
            const close = () => {
                ok.onclick = cancel.onclick = null;
                dialog.close();
                resolve();
            };
            cancel.onclick = close;
            dialog.oncancel = (e) => { if (ok.disabled && !ok.hidden) e.preventDefault(); };

            ok.onclick = async () => {
                ok.disabled = true;
                cancel.disabled = true;
                status.hidden = false;
                const onStatus = (text) => { status.textContent = text; };

                try {
                    const signature = await run(onStatus);
                    status.classList.add("ok");
                    status.replaceChildren("✓ Confirmed. ",
                        el("a", { href: explorerTx(signature), target: "_blank", rel: "noopener" }, "View on Solscan"));
                    done?.();
                    loadTokens();
                    window.gnomeRefresh?.();
                } catch (error) {
                    status.classList.add("bad");
                    const message = /reject|cancel|denied/i.test(error.message || "")
                        ? "You cancelled in the wallet. Nothing was sent."
                        : error.message || String(error);
                    status.textContent = message;
                }
                ok.hidden = true;
                cancel.disabled = false;
                cancel.textContent = "Close";
            };

            dialog.showModal();
        });
    }

    // ---------- Wiring ----------

    $("dapp-network").value = state.network;
    $("dapp-network").addEventListener("change", (event) => {
        state.network = event.target.value;
        writeSetting("network", state.network);
        renderConnection();
        loadTokens();
    });

    $("dapp-connect").addEventListener("click", () => (state.owner ? disconnect() : connect()));
    $("dapp-reload").addEventListener("click", loadTokens);

    $("dapp-track").addEventListener("click", async () => {
        try {
            await window.gnomeApi("/api/wallets", {
                method: "POST",
                body: JSON.stringify({ chain: "solana", address: state.owner.toBase58(), label: `${walletName(state.provider)} wallet` }),
            });
            window.gnomeRefresh?.();
            toast("Added to your portfolio.");
        } catch (error) {
            toast(error.message, true);
        }
    });

    // Solana closed the API faucet, so copy the address and open the web faucet.
    $("dapp-airdrop").addEventListener("click", async () => {
        if (!state.owner) return toast("Connect a wallet first.", true);
        try {
            await navigator.clipboard.writeText(state.owner.toBase58());
            toast("Address copied. Paste it into the faucet, choose Devnet, then press Reload here.");
        } catch {
            toast(`Your address: ${state.owner.toBase58()}`);
        }
        window.open("https://faucet.solana.com", "_blank", "noopener");
    });

    document.querySelectorAll(".dapp .tabs button").forEach((tab) => tab.addEventListener("click", () => {
        document.querySelectorAll(".dapp .tabs button").forEach((b) => b.classList.toggle("active", b === tab));
        document.querySelectorAll(".dapp .tab").forEach((pane) => (pane.hidden = pane.dataset.pane !== tab.dataset.tab));
    }));

    $("send-form").addEventListener("submit", reviewSend);
    $("send-token").addEventListener("change", updateSendHint);
    $("send-max").addEventListener("click", () => {
        const token = tokenByMint($("send-token").value);
        if (token) $("send-form").amount.value = fromBaseUnits(maxSendable(token), token.decimals);
    });

    $("swap-form").addEventListener("submit", reviewSwap);
    $("swap-form").amount.addEventListener("input", scheduleQuote);
    for (const id of ["swap-from", "swap-to", "swap-slippage"]) $(id).addEventListener("change", scheduleQuote);
    $("swap-mint").addEventListener("input", scheduleQuote);
    $("swap-max").addEventListener("click", () => {
        const token = tokenByMint($("swap-from").value);
        if (token) {
            $("swap-form").amount.value = fromBaseUnits(maxSendable(token), token.decimals);
            scheduleQuote();
        }
    });
    $("swap-flip").addEventListener("click", () => {
        const from = $("swap-from").value;
        const to = $("swap-to").value;
        if (tokenByMint(to)) {
            $("swap-from").value = to;
            $("swap-to").value = from;
            $("swap-mint").value = "";
            scheduleQuote();
        } else {
            toast("You don't hold that token yet, so it can't be the one you pay with.", true);
        }
    });

    renderConnection();
    if (readSetting("autoconnect", null)) {
        // Wallet extensions inject a moment after the page loads.
        setTimeout(() => connect(true), 300);
    }

    // For tests and curious developers.
    window.gnomeDapp = { state, toBaseUnits, fromBaseUnits, buildSend, connect };
})();
