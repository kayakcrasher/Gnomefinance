# dashboard.py

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui_data import GUIData
from chart_data import ChartData


class Dashboard:
    """GNOMEfinance main dashboard."""

    def __init__(self, root):
        self.root = root
        self.root.title("GNOMEfinance")
        self.root.geometry("900x700")

        self.data = GUIData()

        self.setup_ui()
        self.load_demo_data()
        self.refresh()

    def setup_ui(self):
        """Create the dashboard interface."""

        title = ttk.Label(
            self.root,
            text="GNOMEfinance",
            font=("Arial", 26, "bold"),
        )
        title.pack(pady=15)

        self.total_label = ttk.Label(
            self.root,
            text="Total: $0.00",
            font=("Arial", 18),
        )
        self.total_label.pack(pady=5)

        self.asset_frame = ttk.Frame(self.root)
        self.asset_frame.pack(
            fill="x",
            padx=30,
            pady=10,
        )

        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10,
        )

        self.refresh_button = ttk.Button(
            self.root,
            text="Refresh",
            command=self.refresh,
        )
        self.refresh_button.pack(pady=15)

    def load_demo_data(self):
        """Load temporary portfolio data."""

        self.data.add_asset("bitcoin", 0.065)
        self.data.add_asset("solana", 5.4)
        self.data.add_asset("cardano", 1500)
        self.data.add_asset("avalanche", 25)

    def clear_chart(self):
        """Remove the previous chart."""

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def create_chart(self):
        """Create the portfolio chart."""

        self.clear_chart()

        portfolio = self.data.portfolio_service.portfolio
        chart_data = ChartData(portfolio)

        data = chart_data.get_chart_data()

        figure = Figure(figsize=(7, 4), dpi=100)
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
        """Refresh dashboard data."""

        for widget in self.asset_frame.winfo_children():
            widget.destroy()

        dashboard = self.data.get_dashboard_data()

        self.total_label.config(
            text=f"Total: ${dashboard['total_value']:,.2f}"
        )

        for network, asset in dashboard["assets"].items():

            row = ttk.Frame(self.asset_frame)
            row.pack(
                fill="x",
                pady=5,
            )

            name = ttk.Label(
                row,
                text=network.upper(),
                font=("Arial", 12, "bold"),
            )
            name.pack(side="left")

            value = ttk.Label(
                row,
                text=f"${asset['value_usd']:,.2f}",
            )
            value.pack(side="right")

        self.create_chart()


def main():
    root = tk.Tk()

    Dashboard(root)

    root.mainloop()


if __name__ == "__main__":
    main()
