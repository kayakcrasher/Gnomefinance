import tkinter as tk
from tkinter import ttk

from .charts import draw_price_chart
from .history import get_history
from .prices import get_price
from .refresh import RefreshController


APP_BG = "#0b1020"
PANEL_BG = "#151c2f"
TEXT = "#f5f7ff"
MUTED = "#9aa6c1"
ACCENT = "#7c5cff"
ERROR = "#ff6b7a"


ASSETS = (
    ("BTC", "bitcoin"),
    ("ETH", "ethereum"),
    ("SOL", "solana"),
)


class GnomeFinanceApp:
    """Main GNOMEfinance desktop application."""

    def __init__(self, root):
        self.root = root
        self.refresh_controller = RefreshController(cooldown=10)
        self.prices = {}

        self.configure_window()
        self.build_styles()
        self.build_layout()

        self.refresh_prices(force=True)

    def configure_window(self):
        self.root.title("GNOMEfinance")
        self.root.geometry("1050x720")
        self.root.minsize(850, 600)
        self.root.configure(bg=APP_BG)

    def build_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "TFrame",
            background=APP_BG,
        )

        style.configure(
            "Panel.TFrame",
            background=PANEL_BG,
        )

        style.configure(
            "Title.TLabel",
            background=APP_BG,
            foreground=TEXT,
            font=("Arial", 25, "bold"),
        )

        style.configure(
            "Subtitle.TLabel",
            background=APP_BG,
            foreground=MUTED,
            font=("Arial", 10),
        )

        style.configure(
            "PanelTitle.TLabel",
            background=PANEL_BG,
            foreground=MUTED,
            font=("Arial", 9, "bold"),
        )

        style.configure(
            "Price.TLabel",
            background=PANEL_BG,
            foreground=TEXT,
            font=("Arial", 19, "bold"),
        )

        style.configure(
            "Symbol.TLabel",
            background=PANEL_BG,
            foreground=ACCENT,
            font=("Arial", 11, "bold"),
        )

        style.configure(
            "Status.TLabel",
            background=APP_BG,
            foreground=MUTED,
            font=("Arial", 9),
        )

        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground=TEXT,
            borderwidth=0,
            padding=(18, 9),
            font=("Arial", 10, "bold"),
        )

        style.map(
            "Accent.TButton",
            background=[
                ("active", "#6848e8"),
            ],
        )

    def build_layout(self):
        header = ttk.Frame(self.root)
        header.pack(
            fill="x",
            padx=28,
            pady=(25, 12),
        )

        title_box = ttk.Frame(header)
        title_box.pack(side="left")

        ttk.Label(
            title_box,
            text="GNOMEfinance",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            title_box,
            text="Your crypto command center",
            style="Subtitle.TLabel",
        ).pack(
            anchor="w",
            pady=(2, 0),
        )

        self.refresh_button = ttk.Button(
            header,
            text="REFRESH",
            style="Accent.TButton",
            command=self.refresh_prices,
        )

        self.refresh_button.pack(
            side="right",
            pady=4,
        )

        self.asset_frame = ttk.Frame(self.root)

        self.asset_frame.pack(
            fill="x",
            padx=28,
            pady=10,
        )

        self.asset_cards = {}

        for symbol, coin_id in ASSETS:
            card = ttk.Frame(
                self.asset_frame,
                style="Panel.TFrame",
                padding=16,
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5,
            )

            ttk.Label(
                card,
                text=symbol,
                style="Symbol.TLabel",
            ).pack(anchor="w")

            ttk.Label(
                card,
                text=coin_id.title(),
                style="PanelTitle.TLabel",
            ).pack(
                anchor="w",
                pady=(4, 8),
            )

            price = ttk.Label(
                card,
                text="Loading...",
                style="Price.TLabel",
            )

            price.pack(anchor="w")

            self.asset_cards[symbol] = price

        chart_panel = ttk.Frame(
            self.root,
            style="Panel.TFrame",
            padding=12,
        )

        chart_panel.pack(
            fill="both",
            expand=True,
            padx=33,
            pady=(10, 8),
        )

        chart_header = ttk.Frame(
            chart_panel,
            style="Panel.TFrame",
        )

        chart_header.pack(
            fill="x",
            padx=8,
            pady=(2, 8),
        )

        ttk.Label(
            chart_header,
            text="BTC • 7 DAY PRICE HISTORY",
            style="PanelTitle.TLabel",
        ).pack(side="left")

        self.chart_frame = ttk.Frame(
            chart_panel,
            style="Panel.TFrame",
        )

        self.chart_frame.pack(
            fill="both",
            expand=True,
        )

        footer = ttk.Frame(self.root)

        footer.pack(
            fill="x",
            padx=33,
            pady=(0, 15),
        )

        self.status = ttk.Label(
            footer,
            text="Ready",
            style="Status.TLabel",
        )

        self.status.pack(side="left")

    def refresh_prices(self, force=False):
        if (
            not force
            and not self.refresh_controller.can_refresh()
        ):
            self.status.configure(
                text="Please wait before refreshing again."
            )
            return

        if not force:
            self.refresh_controller.refresh()

        self.refresh_button.configure(
            state="disabled"
        )

        self.status.configure(
            text="Updating market data..."
        )

        self.root.update_idletasks()

        try:
            for symbol, coin_id in ASSETS:
                price = get_price(coin_id)

                self.prices[symbol] = price

                self.asset_cards[symbol].configure(
                    text=f"${price:,.2f}"
                )

            history = get_history(
                "bitcoin",
                days=7,
            )

            self.draw_chart(history)

            self.status.configure(
                text="Market data updated successfully."
            )

        except Exception as error:
            self.status.configure(
                text=f"Update failed: {error}",
                foreground=ERROR,
            )

        finally:
            self.refresh_button.configure(
                state="normal"
            )

    def draw_chart(self, history):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        draw_price_chart(
            self.chart_frame,
            history,
        )


def start_gui():
    """Launch the GNOMEfinance graphical application."""

    root = tk.Tk()

    GnomeFinanceApp(root)

    root.mainloop()


if __name__ == "__main__":
    start_gui()
