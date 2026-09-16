import tkinter as tk

from .window import create_window


def start_gui():
    window = create_window()

    title = tk.Label(
        window,
        text="GNOMEfinance",
        font=("Arial", 20)
    )

    title.pack(pady=20)

    bitcoin = tk.Label(
        window,
        text="BTC: Loading..."
    )

    bitcoin.pack()

    ethereum = tk.Label(
        window,
        text="ETH: Loading..."
    )

    ethereum.pack()

    solana = tk.Label(
        window,
        text="SOL: Loading..."
    )

    solana.pack()

    window.mainloop()
