import math
import os
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from .bsm import greeks

def delta_heatmap(
    S0: float = 20000.0,
    r: float = 0.06,
    q: float = 0.01,
    sigma: float = 0.20,
    m_start: float = 0.8,
    m_end: float = 1.2,
    m_steps: int = 9,
    t_start: float = 0.1,
    t_end: float = 1.0,
    t_steps: int = 10,
):
    m_grid = np.round(np.linspace(m_start, m_end, int(m_steps)), 4)
    t_grid = np.round(np.linspace(t_start, t_end, int(t_steps)), 4)
    heatmap = pd.DataFrame(index=m_grid, columns=t_grid, dtype=float)
    for m in m_grid:
        K = S0 / m
        for T in t_grid:
            heatmap.loc[m, T] = greeks(S0, K, T, r, q, sigma, "call")["delta"]
    heatmap.index.name = "moneyness(S/K)"
    heatmap.columns.name = "tenor(years)"
    return heatmap


def plot_delta_heatmap(
    heatmap: pd.DataFrame,
    png_path: str | os.PathLike = "outputs/delta_heatmap.png",
    title: str = "Delta heatmap (moneyness × tenor)",
    fmt: str = ".3f",
    cmap: str = "RdYlGn",
):
    """Render a moneyness × tenor delta heatmap to a PNG image."""

    import matplotlib.pyplot as plt
    import seaborn as sns

    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    sns.heatmap(
        heatmap.astype(float),
        annot=True,
        fmt=fmt,
        cmap=cmap,
        cbar_kws={"label": "Delta"},
    )
    plt.title(title)
    plt.xlabel(heatmap.columns.name or "tenor(years)")
    plt.ylabel(heatmap.index.name or "moneyness(S/K)")
    plt.tight_layout()
    plt.savefig(png_path, dpi=200)
    plt.close()
    return png_path

def scenario_table(S0=20000.0, K_atm=20000.0, T=0.25, q=0.01,
                   sigmas=(0.15, 0.20, 0.25), rates=(0.05, 0.06, 0.07)):
    rows = []
    for s in sigmas:
        for r in rates:
            g = greeks(S0, K_atm, T, r, q, s, "call")
            out = {"sigma": s, "rate": r}
            out.update({k: float(round(v, 8)) for k, v in g.items()})
            rows.append(out)
    return pd.DataFrame(rows)

def _load_price_path(
    data_path: str | os.PathLike,
    price_col: str = "Close",
    date_col: Optional[str] = None,
) -> Iterable[float]:
    """Load and clean a price path from CSV (e.g., real NIFTY closes)."""

    df = pd.read_csv(data_path)
    if date_col and date_col in df.columns:
        df = df.sort_values(date_col)

    if price_col not in df.columns:
        raise ValueError(f"Price column '{price_col}' not found in {data_path}")

    prices = df[price_col].dropna().astype(float).reset_index(drop=True)
    if prices.empty:
        raise ValueError(f"No prices available in column '{price_col}' of {data_path}")
    return prices


def delta_hedge_example(
    days: int = 60,
    S0: float = 20000.0,
    K_atm: float = 20000.0,
    T: float = 0.25,
    r: float = 0.06,
    q: float = 0.01,
    sigma: float = 0.20,
    seed: int = 42,
    data_path: str | os.PathLike | None = None,
    price_col: str = "Close",
    date_col: Optional[str] = "Date",
):
    if data_path:
        prices = _load_price_path(data_path, price_col=price_col, date_col=date_col)
        S_path = list(prices)
        days = max(len(S_path) - 1, 1)
        S0 = S_path[0]
    else:
        np.random.seed(seed)
        S_path = [S0]
        mu = r - q
        dt = T / max(days, 1)
        for _ in range(days):
            z = np.random.normal()
            S_next = S_path[-1] * math.exp((mu - 0.5 * sigma ** 2) * dt + sigma * math.sqrt(dt) * z)
            S_path.append(S_next)

    dt = T / max(days, 1)
    df = pd.DataFrame({"day": range(len(S_path)), "S": S_path})
    df["T_years"] = np.maximum(T - df["day"] * dt, 1e-6)
    gdf = df.apply(
        lambda row: greeks(row["S"], K_atm, row["T_years"], r, q, sigma, "call"),
        axis=1,
        result_type="expand",
    )
    sim = pd.concat([df, gdf], axis=1)

    sim["delta_shares"] = -sim["delta"].shift(1).fillna(0.0)
    sim["dS"] = sim["S"].diff().fillna(0.0)
    sim["hedge_pnl"] = sim["delta_shares"] * sim["dS"]
    sim["option_pnl"] = sim["price"] - sim["price"].iloc[0]
    sim["total_pnl"] = sim["option_pnl"] + sim["hedge_pnl"].cumsum()

    return sim[[
        "day",
        "S",
        "price",
        "delta",
        "delta_shares",
        "hedge_pnl",
        "option_pnl",
        "total_pnl",
    ]]
