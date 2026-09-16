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

    window.mainloop()
