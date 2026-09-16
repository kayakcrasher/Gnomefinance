import tkinter as tk

from .window import create_window
from .prices import get_price
from .refresh import RefreshController


def start_gui():
    window = create_window()

    refresh_controller = RefreshController(cooldown=10)

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

    status = tk.Label(
        window,
        text="Ready"
    )

    status.pack(pady=10)

    def refresh_prices():
        if not refresh_controller.can_refresh():
            status.config(
                text="Please wait before refreshing again."
            )
            return

        refresh_controller.last_refresh = 0
        refresh_controller.refresh()

        status.config(text="Updating prices...")

        try:
            bitcoin_price = get_price("bitcoin")
            ethereum_price = get_price("ethereum")
            solana_price = get_price("solana")

            bitcoin.config(
                text=f"BTC: ${bitcoin_price:,.2f}"
            )

            ethereum.config(
                text=f"ETH: ${ethereum_price:,.2f}"
            )

            solana.config(
                text=f"SOL: ${solana_price:,.2f}"
            )

            status.config(text="Prices updated!")

        except Exception as error:
            status.config(
                text=f"Error: {error}"
            )

    refresh_button = tk.Button(
        window,
        text="REFRESH",
        command=refresh_prices
    )

    refresh_button.pack(pady=20)

    refresh_prices()

    window.mainloop()
