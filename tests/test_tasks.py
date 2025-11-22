import pandas as pd

from pathlib import Path

from greeks_engine.tasks import delta_heatmap, delta_hedge_example, plot_heatmap


def test_delta_hedge_uses_real_data_path(tmp_path):
    price_path = tmp_path / "nifty_prices.csv"
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=5, freq="D"),
            "Close": [20000.0, 20050.0, 20100.0, 20080.0, 20120.0],
        }
    )
    data.to_csv(price_path, index=False)

    sim = delta_hedge_example(days=4, data_path=price_path, K_atm=None)

    assert sim["S"].iloc[0] == data["Close"].iloc[0]
    assert sim["S"].tolist() == data["Close"].tolist()
    assert sim["T_years"].iloc[1] < sim["T_years"].iloc[0]
    assert sim["delta_shares"].iloc[0] == 0.0


def test_heatmap_plot_writes_png(tmp_path):
    heatmap_df = delta_heatmap(m_steps=3, t_steps=3)
    png_path = tmp_path / "heatmap.png"

    plot_heatmap(heatmap_df, png_path)

    assert png_path.exists()
    assert png_path.stat().st_size > 0


def test_delta_hedge_with_real_nifty_sample():
    data_path = Path(__file__).resolve().parents[1] / "data" / "nifty_2020_mar_apr.csv"

    sim = delta_hedge_example(days=None, data_path=data_path, K_atm=None, T=0.25)

    assert len(sim) == 39
    assert sim["S"].iloc[0] == 11303.30
    assert sim["S"].iloc[-1] == 9859.90
    assert sim["T_years"].iloc[-1] < sim["T_years"].iloc[0]
    assert sim["hedge_pnl"].abs().sum() > 0
