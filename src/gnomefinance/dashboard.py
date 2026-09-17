# dashboard.py

import tkinter as tk
from tkinter import ttk

from gui_data import GUIData


class Dashboard:
    """GNOMEfinance main dashboard."""

    def __init__(self, root):
        self.root = root
        self.root.title("GNOMEfinance")
        self.root.geometry("700x500")

        self.data = GUIData()

        self.setup_ui()
        self.load_demo_data()
        self.refresh()

    def setup_ui(self):
        """Create the dashboard interface."""

        title = ttk.Label(
            self.root,
            text="GNOMEfinance",
            font=("Arial", 24, "bold"),
        )

        title.pack(pady=20)

        self.total_label = ttk.Label(
            self.root,
            text="Total: $0.00",
            font=("Arial", 18),
        )

        self.total_label.pack(pady=10)

        self.asset_frame = ttk.Frame(self.root)
        self.asset_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20,
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
            row.pack(fill="x", pady=8)

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


def main():
    root = tk.Tk()

    Dashboard(root)

    root.mainloop()


if __name__ == "__main__":
    main()
