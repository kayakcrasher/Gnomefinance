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
from portfolio_storage import PortfolioStorage
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
        self.storage = PortfolioStorage()

        self.setup_ui()
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

        set_button = ttk.Button(
            editor,
            text="Set Holding",
            command=self.set_holding,
        )

        set_button.grid(
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

        save_button = ttk.Button(
            editor,
            text="Save Portfolio",
            command=self.save_portfolio,
        )

        save_button.grid(
            row=1,
            column=4,
            padx=5,
            pady=5,
        )

        load_button = ttk.Button(
            editor,
            text="Load Portfolio",
            command=self.load_portfolio,
        )

        load_button.grid(
            row=1,
            column=5,
            padx=5,
            pady=5,
        )

    def get_portfolio(self):
        """Return the application's portfolio."""

        return (
            self.data
            .portfolio_service
            .portfolio
        )

    def get_input_handler(self):
        """Return a portfolio input handler."""

        return PortfolioInput(
            self.get_portfolio()
        )

    def get_selected_network(self):
        """Return the selected network ID."""

        return self.network_var.get().lower()

    def set_holding(self):
        """Set an exact portfolio holding."""

        try:

            amount = float(
                self.amount_var.get()
            )

            network = (
                self.get_selected_network()
            )

            inputs = self.get_input_handler()

            inputs.set_asset(
                network,
                amount,
            )

            self.amount_var.set("")

            self.save_portfolio(
                show_message=False
            )

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

        inputs = self.get_input_handler()

        inputs.remove_asset(
            network
        )

        self.save_portfolio(
            show_message=False
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

        inputs = self.get_input_handler()

        inputs.clear()

        self.save_portfolio(
            show_message=False
        )

        self.force_refresh()

    def save_portfolio(
        self,
        show_message=True,
    ):
        """Save the current portfolio."""

        try:

            self.storage.save(
                self.get_portfolio()
            )

            self.status_label.config(
                text="Portfolio saved"
            )

            if show_message:

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

            loaded = self.storage.load(
                self.get_portfolio()
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

        portfolio = self.get_portfolio()

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

    def update_dashboard(self):
        """Update the dashboard display."""

        self.status_label.config(
            text="Refreshing market data..."
        )

        self.refresh_button.config(
            state="disabled"
        )

        self.root.update_idletasks()

        try:

            dashboard = (
                self.data
                .get_dashboard_data()
            )

            networks = list(
                dashboard["assets"].keys()
            )

            market_data = (
                self.market
                .get_market_data
