import tkinter as tk

from .window import create_window
from .prices import get_price


def start_gui():
    window = create_window()

    title = tk.Label(
        window,
        text="GNOMEfinance",
        font=("Arial", 20)
    )

    title.pack(pady=20)

    bitcoin = tk.Label(window, text="BTC: Loading...")
    bitcoin.pack()

    ethereum = tk.Label(window, text="ETH: Loading...")
    ethereum.pack()

    solana = tk.Label(window, text="SOL: Loading...")
    solana.pack()

    bitcoin_price = get_price("bitcoin")
    ethereum_price = get_price("ethereum")
    solana_price = get_price("solana")

    bitcoin.config(text=f"BTC: ${bitcoin_price:,.2f}")
    ethereum.config(text=f"ETH: ${ethereum_price:,.2f}")
    solana.config(text=f"SOL: ${solana_price:,.2f}")

    window.mainloop()
