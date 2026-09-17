# dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui_data import GUIData
from chart_data import ChartData
from market_data import MarketData
from portfolio_allocation import PortfolioAllocation
from portfolio_input import PortfolioInput
from asset_card import AssetCard
from network_config import NETWORKS


class Dashboard:
    """GNOMEfinance main dashboard."""

    def __init__(self, root):
        self.root = root
        self.root.title("GNOMEfinance")
        self.root.geometry("1000x900")

        self.data = GUIData()
        self.market = MarketData()

        self.setup_ui()
        self.load_demo_data()
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

        add_button = ttk.Button(
            editor,
            text="Set Holding",
            command=self.set_holding,
        )

        add_button.grid(
            row=0,
            column=4,
            padx=5,
            pady=5,
        )

        remove_button = ttk.Button(
            editor,
            text="Remove Asset",
            command=self.remove_holding,
        )

        remove_button.grid(
            row=0,
            column=5,
            padx=5,
            pady=5,
        )

        clear_button = ttk.Button(
            editor,
            text="Clear Portfolio",
            command=self.clear_portfolio,
        )

        clear_button.grid(
            row=0,
            column=6,
            padx=5,
            pady=5,
        )

    def load_demo_data(self):
        """Load temporary portfolio data."""

        self.data.add_asset(
            "bitcoin",
            0.065,
        )

        self.data.add_asset(
            "solana",
            5.4,
        )

        self.data.add_asset(
            "cardano",
            1500,
        )

        self.data.add_asset(
            "avalanche",
            25,
        )

    def get_selected_network(self):
        """Return the selected network ID."""

        selected = self.network_var.get()

        return selected.lower()

    def set_holding(self):
        """Set an exact portfolio holding."""

        try:
            amount = float(
                self.amount_var.get()
            )

            network = (
                self.get_selected_network()
            )

            portfolio = (
                self.data
                .portfolio_service
                .portfolio
            )

            inputs = PortfolioInput(
                portfolio
            )

            inputs.set_asset(
                network,
                amount,
            )

            self.amount_var.set("")

            self.force_refresh()

        except ValueError as error:

            messagebox.showerror(
                "Invalid Holding",
                str(error),
            )

    def remove_holding(self):
        """Remove the selected asset."""

        network = (
            self.get_selected_network()
        )

        portfolio = (
            self.data
            .portfolio_service
            .portfolio
        )

        inputs = PortfolioInput(
            portfolio
        )

        inputs.remove_asset(
            network
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

        portfolio = (
            self.data
            .portfolio_service
            .portfolio
        )

        inputs = PortfolioInput(
            portfolio
        )

        inputs.clear()

        self.force_refresh()

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
        """Create cards for portfolio assets."""

        self.clear_assets()

        for network, asset in (
            dashboard["assets"].items()
        ):

            info = market_data.get(
                network
            )

            allocation = allocation_data.get(
                network,
                {},
            )

            if info is None:
                price = 0
                change = 0
            else:
                price = info.get(
                    "price",
                    0,
                )

                change = info.get(
                    "change_24h",
                    0,
                )

            percentage = allocation.get(
                "percentage",
                0,
            )

            card = AssetCard(
                self.asset_frame,
                name=network,
                amount=asset["amount"],
                value=asset["value_usd"],
                price=price,
                change_24h=change,
                percentage=percentage,
            )

            card.pack(
                fill="x",
                pady=5,
            )

    def create_chart(self):
        """Create the portfolio chart."""

        self.clear_chart()

        portfolio = (
            self.data
            .portfolio_service
            .portfolio
        )

        chart_data = ChartData(
            portfolio
        )

        data = chart_data.get_chart_data()

        if not data["values"]:
            return

        figure = Figure(
            figsize=(8, 4),
            dpi=100,
        )

        axis = figure.add_subplot(111)

        axis.bar(
            data["labels"],
            data["values"],
        )

        axis.set_title(
            "GNOMEfinance Portfolio Value"
        )

        axis.set_ylabel("USD")

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(
            figure,
            master=self.chart_frame,
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
        )

    def refresh(self):
        """Refresh using cached market data."""

        self.update_dashboard()

    def force_refresh(self):
        """Clear cache and fetch fresh market data."""

        self.market.clear_cache()

        self.update_dashboard()

    def update
