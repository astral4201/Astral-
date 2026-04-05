"""Pivot point (significant high/low) detection."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


def find_pivots(
    df: pd.DataFrame,
    window: int = 20,
) -> tuple[list[tuple[date, float]], list[tuple[date, float]]]:
    """Find significant pivot highs and lows using a rolling window.

    A pivot high is a bar whose High is the highest of the surrounding `window` bars.
    A pivot low is a bar whose Low is the lowest of the surrounding `window` bars.

    Returns (highs, lows) as lists of (date, price).
    """
    highs_list: list[tuple[date, float]] = []
    lows_list: list[tuple[date, float]] = []

    high_col = df["High"].values if "High" in df.columns else df["Close"].values
    low_col = df["Low"].values if "Low" in df.columns else df["Close"].values
    dates = df.index

    for i in range(window, len(df) - window):
        # Pivot High
        local_highs = high_col[i - window : i + window + 1]
        if high_col[i] == np.max(local_highs):
            dt = dates[i]
            if hasattr(dt, "date"):
                dt = dt.date()
            highs_list.append((dt, float(high_col[i])))

        # Pivot Low
        local_lows = low_col[i - window : i + window + 1]
        if low_col[i] == np.min(local_lows):
            dt = dates[i]
            if hasattr(dt, "date"):
                dt = dt.date()
            lows_list.append((dt, float(low_col[i])))

    return highs_list, lows_list
