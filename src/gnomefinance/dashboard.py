# dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app_controller import AppController
from chart_data import ChartData
from asset_card import AssetCard
from network_config import NETWORKS


class Dashboard:
    """GNOMEfinance main dashboard."""

    def __init__(self, root):
        self.root = root
        self.root.title("GNOMEfinance")
        self.root.geometry("1000x900")

        # The controller handles application logic.
        self.controller = AppController()

        self.setup_ui()

        # Try to restore the user's saved portfolio.
        self.load_portfolio()

        self.refresh()

    def setup_ui(self):
        """Create the dashboard interface."""

        title = ttk.Label(
            self.root,
            text="GNOMEfinance",
            font=("Arial", 28, "bold"),
        )

        title.pack(pady=15)

        self.status_label = ttk.Label(
            self.root,
            text="Ready",
        )

        self.status_label.pack()

        self.total_label = ttk.Label(
            self.root,
            text="Total Portfolio: $0.00",
            font=("Arial", 20),
        )

        self.total_label.pack(pady=5)

        self.setup_portfolio_editor()

        self.asset_frame = ttk.Frame(
            self.root
        )

        self.asset_frame.pack(
            fill="x",
            padx=25,
            pady=15,
        )

        self.chart_frame = ttk.Frame(
            self.root
        )

        self.chart_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10,
        )

        self.refresh_button = ttk.Button(
            self.root,
            text="Refresh Market Data",
            command=self.force_refresh,
        )

        self.refresh_button.pack(
            pady=15
        )

    def setup_portfolio_editor(self):
        """Create portfolio editing controls."""

        editor = ttk.LabelFrame(
            self.root,
            text="Portfolio Editor",
            padding=10,
        )

        editor.pack(
            fill="x",
            padx=25,
            pady=10,
        )

        ttk.Label(
            editor,
            text="Asset:",
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
        )

        self.network_var = tk.StringVar()

        self.network_box = ttk.Combobox(
            editor,
            textvariable=self.network_var,
            state="readonly",
            width=15,
        )

        self.network_box["values"] = [
            network.upper()
            for network in NETWORKS
        ]

        self.network_box.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
        )

        self.network_box.current(0)

        ttk.Label(
            editor,
            text="Amount:",
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=5,
        )

        self.amount_var = tk.StringVar()

        self.amount_entry = ttk.Entry(
            editor,
            textvariable=self.amount_var,
            width=15,
        )

        self.amount_entry.grid(
            row=0,
            column=3,
            padx=5,
            pady=5,
        )

        ttk.Button(
            editor,
            text="Set Holding",
            command=self.set_holding,
        ).grid(
            row=0,
            column=4,
            padx=5,
            pady=5,
        )

        ttk.Button(
            editor,
            text="Remove Asset",
            command=self.remove_holding,
        ).grid(
            row=0,
            column=5,
            padx=5,
            pady=5,
        )

        ttk.Button(
            editor,
            text="Clear Portfolio",
            command=self.clear_portfolio,
        ).grid(
            row=0,
            column=6,
            padx=5,
            pady=5,
        )

        ttk.Button(
            editor,
            text="Save Portfolio",
            command=self.save_portfolio,
        ).grid(
            row=1,
            column=4,
            padx=5,
            pady=5,
        )

        ttk.Button(
            editor,
            text="Load Portfolio",
            command=self.load_portfolio,
        ).grid(
            row=1,
            column=5,
            padx=5,
            pady=5,
        )

    def get_selected_network(self):
        """Return the selected network."""

        return self.network_var.get().lower()

    def set_holding(self):
        """Set an asset holding."""

        try:
            network = self.get_selected_network()

            amount = float(
                self.amount_var.get()
            )

            self.controller.set_holding(
                network,
                amount,
            )

            self.amount_var.set("")

            self.controller.save_portfolio()

            self.status_label.config(
                text="Holding updated and saved"
            )

            self.force_refresh()

        except ValueError as error:

            messagebox.showerror(
                "Invalid Holding",
                str(error),
            )

    def remove_holding(self):
        """Remove the selected asset."""

        network = self.get_selected_network()

        self.controller.remove_holding(
            network
        )

        self.controller.save_portfolio()

        self.status_label.config(
            text="Asset removed and portfolio saved"
        )

        self.force_refresh()

    def clear_portfolio(self):
        """Clear the entire portfolio."""

        confirm = messagebox.askyesno(
            "Clear Portfolio",
            "Remove all portfolio holdings?",
        )

        if not confirm:
            return

        self.controller.clear_portfolio()

        self.controller.save_portfolio()

        self.status_label.config(
            text="Portfolio cleared"
        )

        self.force_refresh()

    def save_portfolio(self):
        """Save the portfolio."""

        try:

            self.controller.save_portfolio()

            self.status_label.config(
                text="Portfolio saved"
            )

            messagebox.showinfo(
                "GNOMEfinance",
                "Portfolio saved successfully.",
            )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error),
            )

    def load_portfolio(self):
        """Load the saved portfolio."""

        try:

            loaded = (
                self.controller
                .load_portfolio()
            )

            if loaded:

                self.status_label.config(
                    text="Portfolio loaded"
                )

            else:

                self.status_label.config(
                    text="No saved portfolio found"
                )

        except Exception as error:

            messagebox.showerror(
                "Load Error",
                str(error),
            )

    def clear_assets(self):
        """Remove existing asset cards."""

        for widget in (
            self.asset_frame.winfo_children()
        ):
            widget.destroy()

    def clear_chart(self):
        """Remove the existing chart."""

        for widget in (
            self.chart_frame.winfo_children()
        ):
            widget.destroy()

    def create_asset_cards(
        self,
        dashboard,
        market_data,
        allocation_data,
    ):
        """Create asset cards."""

        self.clear_assets()

        for network, asset in (
            dashboard["assets"].items()
        ):

            market = market_data.get(
                network,
                {},
            )

            allocation = allocation_data.get(
                network,
                {},
            )

            card = AssetCard(
                self.asset_frame,
                name=network,
                amount=asset["amount"],
                value=asset["value_usd"],
                price=market.get(
                    "price",
                    0,
                ),
                change_24h=market.get(
                    "change_24h",
                    0,
                ),
                percentage=allocation.get(
                    "percentage",
                    0,
                ),
            )

            card.pack(
                fill="x",
                pady=5,
            )

    def create_chart(self):
        """Create the portfolio chart."""

        self.clear_chart()

        portfolio = (
            self.controller
            .get_portfolio()
        )

       
