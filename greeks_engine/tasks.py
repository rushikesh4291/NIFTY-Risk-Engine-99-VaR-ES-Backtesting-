import math
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

def delta_hedge_example(days=60, S0=20000.0, K_atm=20000.0, T=0.25, r=0.06, q=0.01, sigma=0.20, seed=42):
    np.random.seed(seed)
    dt = 1/252
    mu = r - q
    S_path = [S0]
    for _ in range(days):
        z = np.random.normal()
        S_next = S_path[-1] * math.exp((mu - 0.5*sigma**2)*dt + sigma*math.sqrt(dt)*z)
        S_path.append(S_next)

    df = pd.DataFrame({"day": range(len(S_path)), "S": S_path})
    df["T_years"] = np.maximum(T - df["day"]*dt, 1e-6)
    gdf = df.apply(lambda row: greeks(row["S"], K_atm, row["T_years"], r, q, sigma, "call"), axis=1, result_type="expand")
    sim = pd.concat([df, gdf], axis=1)

    sim["delta_shares"] = -sim["delta"].shift(1).fillna(0.0)
    sim["dS"] = sim["S"].diff().fillna(0.0)
    sim["hedge_pnl"] = sim["delta_shares"] * sim["dS"]
    sim["option_pnl"] = sim["price"] - sim["price"].iloc[0]
    sim["total_pnl"] = sim["option_pnl"] + sim["hedge_pnl"].cumsum()

    return sim[["day","S","price","delta","delta_shares","hedge_pnl","option_pnl","total_pnl"]]
