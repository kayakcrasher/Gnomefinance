# dashboard.py

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui_data import GUIData
from chart_data import ChartData
from market_data import MarketData
from asset_card import AssetCard


class Dashboard:
    """GNOMEfinance main dashboard."""

    def __init__(self, root):
        self.root = root
        self.root.title("GNOMEfinance")
        self.root.geometry("1000x800")

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

        self.total_label = ttk.Label(
            self.root,
            text="Total: $0.00",
            font=("Arial", 20),
        )
        self.total_label.pack(pady=5)

        self.asset_frame = ttk.Frame(self.root)
        self.asset_frame.pack(
            fill="x",
            padx=25,
            pady=15,
        )

        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10,
        )

        self.refresh_button = ttk.Button(
            self.root,
            text="Refresh Market Data",
            command=self.refresh,
        )
        self.refresh_button.pack(pady=15)

    def load_demo_data(self):
        """Load temporary portfolio data."""

        self.data.add_asset("bitcoin", 0.065)
        self.data.add_asset("solana", 5.4)
        self.data.add_asset("cardano", 1500)
        self.data.add_asset("avalanche", 25)

    def clear_assets(self):
        """Remove existing asset cards."""

        for widget in self.asset_frame.winfo_children():
            widget.destroy()

    def clear_chart(self):
        """Remove the existing chart."""

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def create_asset_cards(self, dashboard, market_data):
        """Create a card for each portfolio asset."""

        self.clear_assets()

        for network, asset in dashboard["assets"].items():

            info = market_data.get(
                network,
                {},
            )

            price = info.get("price", 0)
            change = info.get("change_24h", 0)

            card = AssetCard(
                self.asset_frame,
                name=network,
                amount=asset["amount"],
                value=asset["value_usd"],
                price=price,
                change_24h=change,
            )

            card.pack(
                fill="x",
                pady=5,
            )

    def create_chart(self):
        """Create the portfolio chart."""

        self.clear_chart()

        portfolio = (
            self.data.portfolio_service.portfolio
        )

        chart_data = ChartData(portfolio)
        data = chart_data.get_chart_data()

        figure = Figure(
            figsize=(8, 4),
            dpi=100,
        )

        axis = figure.add_subplot(111)

        axis.bar(
            data["labels"],
            data["values"],
        )

        axis.set_title("Portfolio Value")
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
        """Refresh the entire dashboard."""

        dashboard = (
            self.data.get_dashboard_data()
        )

        networks = list(
            dashboard["assets"].keys()
        )

        market_data = (
            self.market.get_market_data(networks)
        )

        self.total_label.config(
            text=(
                f"Total Portfolio: "
                f"${dashboard['total_value']:,.2f}"
            )
        )

        self.create_asset_cards(
            dashboard,
            market_data,
        )

        self.create_chart()


def main():
    root = tk.Tk()

    Dashboard(root)

    root.mainloop()


if __name__ == "__main__":
    main()
