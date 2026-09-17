# asset_card.py

import tkinter as tk
from tkinter import ttk


class AssetCard(ttk.Frame):
    """Reusable GNOMEfinance asset card."""

    def __init__(
        self,
        parent,
        name,
        amount,
        value,
        price,
        change_24h,
    ):
        super().__init__(
            parent,
            padding=12,
            relief="ridge",
            borderwidth=1,
        )

        self.name = name
        self.amount = amount
        self.value = value
        self.price = price
        self.change_24h = change_24h

        self.build()

    def build(self):
        """Build the asset card."""

        header = ttk.Label(
            self,
            text=self.name.upper(),
            font=("Arial", 12, "bold"),
        )

        header.grid(
            row=0,
            column=0,
            sticky="w",
        )

        amount_label = ttk.Label(
            self,
            text=f"Holdings: {self.amount:g}",
        )

        amount_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=3,
        )

        price_label = ttk.Label(
            self,
            text=f"Price: ${self.price:,.2f}",
        )

        price_label.grid(
            row=2,
            column=0,
            sticky="w",
            pady=3,
        )

        value_label = ttk.Label(
            self,
            text=f"Value: ${self.value:,.2f}",
            font=("Arial", 11, "bold"),
        )

        value_label.grid(
            row=3,
            column=0,
            sticky="w",
            pady=3,
        )

        change_label = ttk.Label(
            self,
            text=f"24h: {self.change_24h:.2f}%",
        )

        change_label.grid(
            row=4,
            column=0,
            sticky="w",
            pady=3,
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("GNOMEfinance Asset Card")

    card = AssetCard(
        root,
        name="Bitcoin",
        amount=0.065,
        value=7000,
        price=100000,
        change_24h=2.5,
    )

    card.pack(
        padx=20,
        pady=20,
        fill="x",
    )

    root.mainloop()
