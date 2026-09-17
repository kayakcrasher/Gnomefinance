# dashboard.py

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui_data import GUIData
from chart_data import ChartData
from market_data import MarketData
from portfolio_allocation import PortfolioAllocation
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
            command=self.refresh,
        )

        self.refresh_button.pack(
            pady=15
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
        """Refresh the dashboard safely."""

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
                .get_market_data(
                    networks
                )
            )

            portfolio = (
                self.data
                .portfolio_service
                .portfolio
            )

            allocation_service = (
                PortfolioAllocation(
                    portfolio
                )
            )

            allocation_data = (
                allocation_service
                .get_summary()
            )

            self.total_label.config(
                text=(
                    "Total Portfolio: "
                    f"${dashboard['total_value']:,.2f}"
                )
            )

            self.create_asset_cards(
                dashboard,
                market_data,
                allocation_data,
            )

            self.create_chart()

            if market_data:
                self.status_label.config(
                    text="Market data updated"
                )
            else:
                self.status_label.config(
                    text=(
                        "Market data unavailable"
                    )
                )

        except Exception as error:

            self.status_label.config(
                text=(
                    "Dashboard refresh failed"
                )
            )

            print(
                "GNOMEfinance dashboard error:",
                error,
            )

        finally:

            self.refresh_button.config(
                state="normal"
            )


def main():
    """Start GNOMEfinance."""

    root = tk.Tk()

    Dashboard(root)

    root.mainloop()


if __name__ == "__main__":
    main()
