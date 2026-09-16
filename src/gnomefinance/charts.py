import tkinter as tk
from tkinter import Canvas


def draw_price_chart(parent, history):
    canvas = Canvas(
        parent,
        width=360,
        height=200
    )

    canvas.pack(pady=20)

    if not history:
        canvas.create_text(
            180,
            100,
            text="No chart data available"
        )
        return canvas

    prices = [point[1] for point in history]

    minimum = min(prices)
    maximum = max(prices)

    if maximum == minimum:
        maximum += 1

    width = 340
    height = 160

    points = []

    for index, price in enumerate(prices):
        x = 10 + (
            index / (len(prices) - 1)
        ) * width

        y = 180 - (
            (price - minimum)
            / (maximum - minimum)
        ) * height

        points.extend([x, y])

    canvas.create_line(
        points,
        width=2
    )

    canvas.create_text(
        10,
        10,
        anchor="nw",
        text=f"${maximum:,.2f}"
    )

    canvas.create_text(
        10,
        180,
        anchor="sw",
        text=f"${minimum:,.2f}"
    )

    return canvas
