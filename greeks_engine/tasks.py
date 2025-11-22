import math
import struct
import zlib
from typing import Optional

import numpy as np
import pandas as pd

from .bsm import greeks

def delta_heatmap(S0=20000.0, r=0.06, q=0.01, sigma=0.20,
                  m_start=0.8, m_end=1.2, m_steps=9,
                  t_start=0.1, t_end=1.0, t_steps=10):
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


def _normalize(values: np.ndarray) -> np.ndarray:
    arr = values.astype(float)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    vmin = np.min(arr)
    vmax = np.max(arr)
    span = vmax - vmin if vmax != vmin else 1.0
    return (arr - vmin) / span


def _viridis_palette() -> np.ndarray:
    # Reduced set of viridis anchor points (RGB 0-255)
    return np.array(
        [
            (68, 1, 84),
            (59, 82, 139),
            (33, 145, 140),
            (94, 201, 98),
            (253, 231, 37),
        ],
        dtype=float,
    )


def _apply_palette(norm_matrix: np.ndarray, palette: np.ndarray) -> np.ndarray:
    positions = np.linspace(0.0, 1.0, len(palette))
    r = np.interp(norm_matrix, positions, palette[:, 0])
    g = np.interp(norm_matrix, positions, palette[:, 1])
    b = np.interp(norm_matrix, positions, palette[:, 2])
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def _write_png(rgb_image: np.ndarray, output_path: str) -> None:
    height, width, _ = rgb_image.shape
    raw = b"".join(b"\x00" + row.tobytes() for row in rgb_image)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(output_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, level=9)))
        f.write(chunk(b"IEND", b""))


def plot_heatmap(heatmap: pd.DataFrame, output_path: str, cmap: str = "viridis") -> None:
    norm = _normalize(heatmap.to_numpy())
    palette = _viridis_palette() if cmap == "viridis" else _viridis_palette()
    rgb_image = _apply_palette(norm, palette)
    _write_png(rgb_image, output_path)

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

def _load_price_path(data_path: str, price_column: str, date_column: Optional[str], days: Optional[int]):
    df = pd.read_csv(data_path)
    if date_column and date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)
    if price_column not in df.columns:
        raise ValueError(f"Price column '{price_column}' not found in {data_path}")

    price_series = df[price_column].astype(float)
    if days is not None:
        price_series = price_series.iloc[: days + 1]
    if len(price_series) < 2:
        raise ValueError("Not enough price points to run hedge simulation")

    if date_column and date_column in df.columns:
        date_series = df[date_column].iloc[: len(price_series)]
        date_diffs = date_series.diff().dt.days.dropna()
        if not date_diffs.empty and (date_diffs > 0).all():
            dt = date_diffs.mean() / 365
        else:
            dt = 1 / 252
    else:
        dt = 1 / 252
    return price_series.tolist(), dt


def delta_hedge_example(days: Optional[int] = 60, S0=20000.0, K_atm: Optional[float] = None, T=0.25,
                        r=0.06, q=0.01, sigma=0.20, seed=42, data_path: Optional[str] = None,
                        price_column: str = "Close", date_column: str = "Date"):
    if data_path:
        S_path, dt = _load_price_path(data_path, price_column, date_column, days)
        if K_atm is None:
            K_atm = S_path[0]
    else:
        if days is None:
            raise ValueError("'days' must be provided when data_path is not set")
        np.random.seed(seed)
        dt = 1 / 252
        mu = r - q
        S_path = [S0]
        for _ in range(days):
            z = np.random.normal()
            S_next = S_path[-1] * math.exp((mu - 0.5 * sigma ** 2) * dt + sigma * math.sqrt(dt) * z)
            S_path.append(S_next)
        if K_atm is None:
            K_atm = S0

    df = pd.DataFrame({"day": range(len(S_path)), "S": S_path})
    df["T_years"] = np.maximum(T - df["day"] * dt, 1e-6)
    gdf = df.apply(lambda row: greeks(row["S"], K_atm, row["T_years"], r, q, sigma, "call"), axis=1, result_type="expand")
    sim = pd.concat([df, gdf], axis=1)

    sim["delta_shares"] = -sim["delta"].shift(1).fillna(0.0)
    sim["dS"] = sim["S"].diff().fillna(0.0)
    sim["hedge_pnl"] = sim["delta_shares"] * sim["dS"]
    sim["option_pnl"] = sim["price"] - sim["price"].iloc[0]
    sim["total_pnl"] = sim["option_pnl"] + sim["hedge_pnl"].cumsum()

    return sim[["day", "T_years", "S", "price", "delta", "delta_shares", "hedge_pnl", "option_pnl", "total_pnl"]]
