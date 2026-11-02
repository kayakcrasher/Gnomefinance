"""GNOMEfinance desktop app (tkinter).

Network calls run on a background thread so the window never freezes;
results are handed back to the UI thread with ``root.after``.
"""

import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from . import assets
from .errors import GNOMEfinanceError
from .service import GnomeFinance

BG = "#0b0f0c"
PANEL = "#121914"
BORDER = "#29362c"
TEXT = "#f1f0e8"
MUTED = "#98a197"
GOLD = "#d5b56a"
GREEN = "#8bb98c"
RED = "#d98a7e"

RANGES = (("1D", 1), ("7D", 7), ("1M", 30), ("3M", 90), ("1Y", 365))
AUTO_REFRESH_MS = 120_000


def usd(value):
    if value is None:
        return "—"
    return f"${value:,.2f}" if abs(value) >= 1 else f"${value:,.6f}"


def trend_color(value):
    return GREEN if value > 0 else RED if value < 0 else MUTED


class GnomeFinanceApp:
    def __init__(self, root, service=None):
        self.root = root
        self.gf = service or GnomeFinance()
        self.chart_asset = "bitcoin"
        self.chart_days = 7
        self.history = []

        self.root.title("GNOMEfinance")
        self.root.geometry("1100x780")
        self.root.minsize(900, 640)
        self.root.configure(bg=BG)

        self.build_styles()
        self.build_layout()
        self.refresh()
        self.root.after(AUTO_REFRESH_MS, self.auto_refresh)

    # ---------- Background work ----------

    def run_async(self, work, done, failed=None):
        """Run ``work()`` on a thread, then ``done(result)`` on the UI thread."""

        def target():
            try:
                result = work()
            except Exception as error:  # noqa: BLE001 - shown to the user
                self.root.after(0, lambda: (failed or self.show_error)(error))
            else:
                self.root.after(0, lambda: done(result))

        threading.Thread(target=target, daemon=True).start()

    def show_error(self, error):
        self.status.configure(text=f"Error: {error}", foreground=RED)

    # ---------- Layout ----------

    def build_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Arial", 10))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Arial", 9))
        style.configure("Title.TLabel", font=("Georgia", 24, "bold"))
        style.configure("Sub.TLabel", foreground=MUTED)
        style.configure("Total.TLabel", font=("Georgia", 30, "bold"))
        style.configure("Price.TLabel", background=PANEL, font=("Arial", 15, "bold"))
        style.configure("Heading.TLabel", background=PANEL, foreground=GOLD, font=("Georgia", 13, "bold"))
        style.configure("TButton", background=PANEL, foreground=TEXT, bordercolor=BORDER, padding=6)
        style.map("TButton", background=[("active", "#1e2a21")])
        style.configure("Accent.TButton", background=GOLD, foreground="#17140d", font=("Arial", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#ead08b")])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                        bordercolor=BORDER, rowheight=26)
        style.configure("Treeview.Heading", background="#18211a", foreground=MUTED)
        style.map("Treeview", background=[("selected", "#2a3a2d")])

    def build_layout(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=24, pady=(20, 8))

        title = ttk.Frame(header)
        title.pack(side="left")
        ttk.Label(title, text="🍄 GNOMEfinance", style="Title.TLabel").pack(anchor="w")
        self.total_label = ttk.Label(title, text="—", style="Total.TLabel")
        self.total_label.pack(anchor="w", pady=(6, 0))
        self.change_label = ttk.Label(title, text="Loading…", style="Sub.TLabel")
        self.change_label.pack(anchor="w")

        self.refresh_button = ttk.Button(
            header, text="REFRESH", style="Accent.TButton",
            command=lambda: self.refresh(force=True),
        )
        self.refresh_button.pack(side="right", anchor="n")

        # Market cards (click one to chart it)
        cards = ttk.Frame(self.root)
        cards.pack(fill="x", padx=24, pady=8)
        self.cards = {}

        for asset_id, info in assets.ASSETS.items():
            card = ttk.Frame(cards, style="Panel.TFrame", padding=12)
            card.pack(side="left", fill="both", expand=True, padx=4)
            name = ttk.Label(card, text=f"{info['icon']} {info['symbol']}", style="Panel.TLabel")
            name.pack(anchor="w")
            price = ttk.Label(card, text="…", style="Price.TLabel")
            price.pack(anchor="w", pady=(6, 0))
            change = ttk.Label(card, text="", style="Muted.TLabel")
            change.pack(anchor="w")
            for widget in (card, name, price, change):
                widget.bind("<Button-1>", lambda _e, a=asset_id: self.select_chart(a))
            self.cards[asset_id] = (price, change)

        # Body: chart on top, holdings + wallets below
        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=24, pady=8)

        chart_panel = ttk.Frame(body, style="Panel.TFrame", padding=12)
        chart_panel.pack(fill="both", expand=True, padx=4, pady=(0, 8))
        chart_head = ttk.Frame(chart_panel, style="Panel.TFrame")
        chart_head.pack(fill="x")
        self.chart_title = ttk.Label(chart_head, text="", style="Heading.TLabel")
        self.chart_title.pack(side="left")
        for label, days in reversed(RANGES):
            ttk.Button(chart_head, text=label, width=4,
                       command=lambda d=days: self.select_range(d)).pack(side="right", padx=2)
        self.canvas = tk.Canvas(chart_panel, bg=PANEL, highlightthickness=0, height=220)
        self.canvas.pack(fill="both", expand=True, pady=(8, 0))
        self.canvas.bind("<Configure>", lambda _e: self.draw_chart())

        lower = ttk.Frame(body)
        lower.pack(fill="both", expand=True)
        self.build_holdings(lower)
        self.build_wallets(lower)

        self.status = ttk.Label(self.root, text="Ready", style="Sub.TLabel")
        self.status.pack(fill="x", padx=28, pady=(0, 12))

    def build_holdings(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        panel.pack(side="left", fill="both", expand=True, padx=4)
        ttk.Label(panel, text="Holdings", style="Heading.TLabel").pack(anchor="w")

        form = ttk.Frame(panel, style="Panel.TFrame")
        form.pack(fill="x", pady=8)
        self.asset_choice = ttk.Combobox(
            form, state="readonly", width=8,
            values=[info["symbol"] for info in assets.ASSETS.values()],
        )
        self.asset_choice.current(0)
        self.asset_choice.pack(side="left")
        self.amount_entry = ttk.Entry(form, width=14)
        self.amount_entry.pack(side="left", padx=6)
        self.amount_entry.bind("<Return>", lambda _e: self.set_holding())
        ttk.Button(form, text="Set", command=self.set_holding).pack(side="left")
        ttk.Button(form, text="Remove", command=self.remove_holding).pack(side="left", padx=6)

        columns = ("amount", "price", "value", "change", "share")
        self.table = ttk.Treeview(panel, columns=columns, show="tree headings", height=6)
        self.table.heading("#0", text="Asset")
        self.table.column("#0", width=80)
        for column, heading in zip(columns, ("Amount", "Price", "Value", "24h", "Share")):
            self.table.heading(column, text=heading)
            self.table.column(column, anchor="e", width=95)
        self.table.tag_configure("up", foreground=GREEN)
        self.table.tag_configure("down", foreground=RED)
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_table_select)

    def build_wallets(self, parent):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        panel.pack(side="left", fill="both", expand=True, padx=4)
        ttk.Label(panel, text="Wallets", style="Heading.TLabel").pack(anchor="w")

        form = ttk.Frame(panel, style="Panel.TFrame")
        form.pack(fill="x", pady=8)
        self.chain_choice = ttk.Combobox(
            form, state="readonly", width=9, values=list(self.gf.chains),
        )
        self.chain_choice.current(0)
        self.chain_choice.pack(side="left")
        self.address_entry = ttk.Entry(form)
        self.address_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.address_entry.bind("<Return>", lambda _e: self.add_wallet())
        ttk.Button(form, text="Track", command=self.add_wallet).pack(side="left")
        ttk.Button(form, text="Remove", command=self.remove_wallet).pack(side="left", padx=(6, 0))

        self.wallet_table = ttk.Treeview(panel, columns=("balance", "address"),
                                         show="tree headings", height=6)
        self.wallet_table.heading("#0", text="Label")
        self.wallet_table.heading("balance", text="Balance")
        self.wallet_table.heading("address", text="Address")
        self.wallet_table.column("#0", width=110)
        self.wallet_table.column("balance", anchor="e", width=120)
        self.wallet_table.column("address", width=180)
        self.wallet_table.pack(fill="both", expand=True)

    # ---------- Data ----------

    def auto_refresh(self):
        self.refresh()
        self.root.after(AUTO_REFRESH_MS, self.auto_refresh)

    def refresh(self, force=False):
        self.refresh_button.configure(state="disabled")
        self.status.configure(text="Updating…", foreground=MUTED)

        def work():
            quotes = {}
            try:
                quotes = self.gf.quotes(force=force)
            except GNOMEfinanceError:
                pass  # summary() reports the error
            return quotes, self.gf.summary()

        def done(result):
            quotes, summary = result
            self.render_market(quotes)
            self.render_summary(summary)
            self.refresh_button.configure(state="normal")
            message = " · ".join(summary["errors"]) or f"Updated {datetime.now():%H:%M:%S}"
            self.status.configure(text=message,
                                  foreground=RED if summary["errors"] else MUTED)

        def failed(error):
            self.refresh_button.configure(state="normal")
            self.show_error(error)

        self.run_async(work, done, failed)
        self.load_chart()

    def render_market(self, quotes):
        for asset_id, (price, change) in self.cards.items():
            quote = quotes.get(asset_id)
            if quote is None:
                price.configure(text="Unavailable")
                change.configure(text="")
                continue
            price.configure(text=usd(quote["price"]))
            change.configure(text=f"{quote['change_24h']:+.2f}% 24h",
                             foreground=trend_color(quote["change_24h"]))

    def render_summary(self, summary):
        self.total_label.configure(text=usd(summary["total_value"]))
        if summary["assets"]:
            sign = "+" if summary["change_24h"] >= 0 else "-"
            self.change_label.configure(
                text=f"{sign}{usd(abs(summary['change_24h']))} "
                     f"({summary['change_24h_pct']:+.2f}%) today",
                foreground=trend_color(summary["change_24h"]),
            )
        else:
            self.change_label.configure(text="Add a holding or wallet to get started.",
                                        foreground=MUTED)

        self.table.delete(*self.table.get_children())
        for row in summary["assets"]:
            tag = "up" if row["change_24h"] > 0 else "down" if row["change_24h"] < 0 else ""
            self.table.insert(
                "", "end", iid=row["asset_id"], text=f"{row['icon']} {row['symbol']}",
                values=(f"{row['amount']:,.8g}", usd(row["price"]), usd(row["value"]),
                        f"{row['change_24h']:+.2f}%", f"{row['allocation']:.1f}%"),
                tags=(tag,),
            )

        self.wallet_table.delete(*self.wallet_table.get_children())
        for wallet in summary["wallets"]:
            balance = ("unavailable" if wallet["balance"] is None
                       else f"{wallet['balance']:,.8g} {wallet['symbol']}")
            self.wallet_table.insert("", "end", iid=wallet["id"], text=wallet["label"],
                                     values=(balance, wallet["address"]))

    def on_table_select(self, _event):
        selection = self.table.selection()
        if not selection:
            return
        asset_id = selection[0]
        self.asset_choice.set(assets.symbol(asset_id))
        self.amount_entry.delete(0, "end")
        manual = self.gf.portfolio.amount(asset_id)
        if manual:
            self.amount_entry.insert(0, f"{manual:g}")

    def selected_asset(self):
        return assets.find_by_symbol(self.asset_choice.get())

    def set_holding(self):
        try:
            self.gf.set_holding(self.selected_asset(), self.amount_entry.get())
        except GNOMEfinanceError as error:
            messagebox.showerror("GNOMEfinance", str(error))
            return
        self.amount_entry.delete(0, "end")
        self.refresh_summary()

    def remove_holding(self):
        self.gf.remove_holding(self.selected_asset())
        self.refresh_summary()

    def add_wallet(self):
        try:
            self.gf.add_wallet(self.chain_choice.get(), self.address_entry.get())
        except GNOMEfinanceError as error:
            messagebox.showerror("GNOMEfinance", str(error))
            return
        self.address_entry.delete(0, "end")
        self.refresh_summary()

    def remove_wallet(self):
        selection = self.wallet_table.selection()
        if not selection:
            messagebox.showinfo("GNOMEfinance", "Select a wallet in the list first.")
            return
        self.gf.remove_wallet(selection[0])
        self.refresh_summary()

    def refresh_summary(self):
        self.run_async(self.gf.summary, self.render_summary)

    # ---------- Chart ----------

    def select_chart(self, asset_id):
        self.chart_asset = asset_id
        self.load_chart()

    def select_range(self, days):
        self.chart_days = days
        self.load_chart()

    def load_chart(self):
        asset_id, days = self.chart_asset, self.chart_days
        label = {d: name for name, d in RANGES}[days]
        self.chart_title.configure(text=f"{assets.get_asset(asset_id)['name']} · {label}")

        def done(points):
            # Ignore slow responses for a chart the user already switched away from.
            if (asset_id, days) == (self.chart_asset, self.chart_days):
                self.history = points
                self.draw_chart()

        def failed(error):
            self.history = []
            self.draw_chart(message=f"Chart unavailable: {error}")

        self.run_async(lambda: self.gf.history(asset_id, days), done, failed)

    def draw_chart(self, message="Loading chart…"):
        canvas = self.canvas
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()

        if len(self.history) < 2 or width < 10:
            canvas.create_text(width / 2, height / 2, text=message, fill=MUTED)
            return

        prices = [p[1] for p in self.history]
        low, high = min(prices), max(prices)
        span = (high - low) or 1
        pad = 18
        color = GREEN if prices[-1] >= prices[0] else RED

        points = []
        for i, price in enumerate(prices):
            points.append(pad + i / (len(prices) - 1) * (width - 2 * pad))
            points.append(pad + (1 - (price - low) / span) * (height - 2 * pad))

        canvas.create_line(*points, fill=color, width=2)
        canvas.create_text(pad, 4, anchor="nw", text=f"High {usd(high)}", fill=MUTED)
        canvas.create_text(pad, height - 4, anchor="sw", text=f"Low {usd(low)}", fill=MUTED)
        change = (prices[-1] - prices[0]) / prices[0] * 100
        canvas.create_text(width - pad, 4, anchor="ne", text=f"{change:+.2f}%", fill=color)


def start_gui():
    """Launch the GNOMEfinance desktop application."""
    root = tk.Tk()
    GnomeFinanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    start_gui()
