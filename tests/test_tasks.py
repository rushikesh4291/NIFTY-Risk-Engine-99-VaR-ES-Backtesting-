from pathlib import Path

import pandas as pd
import pytest

from greeks_engine.tasks import delta_heatmap, delta_hedge_example, plot_delta_heatmap


def test_delta_heatmap_generates_grid(tmp_path):
    pytest.importorskip("matplotlib")
    pytest.importorskip("seaborn")

    df = delta_heatmap(S0=20000, sigma=0.2, m_steps=5, t_steps=4)

    assert df.shape == (5, 4)
    assert df.index.name == "moneyness(S/K)"
    assert df.columns.name == "tenor(years)"

    png_path = tmp_path / "heatmap.png"
    plotted = plot_delta_heatmap(df, png_path=png_path)
    assert plotted.exists()


def test_delta_hedge_with_real_prices(tmp_path):
    data_path = Path(__file__).parent / "data" / "nifty_sample.csv"
    sim = delta_hedge_example(
        T=0.05,
        K_atm=9000,
        r=0.06,
        q=0.01,
        sigma=0.25,
        data_path=data_path,
        price_col="Close",
        date_col="Date",
    )

    input_prices = pd.read_csv(data_path)["Close"].tolist()
    assert sim["S"].tolist() == pytest.approx(input_prices)
    assert len(sim) == len(input_prices)
    assert sim[["price", "delta", "total_pnl"]].notna().all().all()
