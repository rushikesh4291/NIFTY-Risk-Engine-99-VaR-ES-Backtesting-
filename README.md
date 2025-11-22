# Options Greeks & Delta-Hedge Engine — Python (BSM)

 Project for pricing European options (Black–Scholes–Merton), computing Greeks, and demonstrating a rolling delta hedge. Ships with CSV outputs and a tiny CLI.

> **Use-cases**
> - Generate moneyness × tenor **Delta heatmaps** (CSV + PNG) for hedge sizing
> - Create **scenario tables** (±σ, ±r) with price + Greeks
> - Run a **toy rolling delta-hedge** path to explain P&L attribution

## Quickstart

```bash
python -V        # 3.10+ recommended
python -m venv .venv && source .venv/bin/activate    # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# 1) Heatmap (CSV + PNG)
python -m greeks_engine.cli heatmap --S 20000 --sigma 0.20 --r 0.06 --q 0.01 --out outputs/delta_heatmap.csv --png-out outputs/delta_heatmap.png

# 2) Scenario table at ATM
python -m greeks_engine.cli scenarios --S 20000 --K 20000 --T 0.25 --out outputs/scenario_table.csv

# 3) Rolling delta hedge (toy, simulated path)
python -m greeks_engine.cli hedge --days 60 --S 20000 --K 20000 --sigma 0.20 --out outputs/delta_hedge_example.csv

# 4) Rolling delta hedge (real NIFTY closes)
#    Put your price history CSV in data/nifty_spot.csv with columns: Date, Close
python -m greeks_engine.cli hedge --data data/nifty_spot.csv --K 20000 --T 0.25 --sigma 0.20 --out outputs/delta_hedge_nifty.csv
```

Outputs land in `outputs/` as CSV, and heatmaps also render to PNG.

## Repo layout

```
greeks_engine/           # package
  bsm.py                 # BSM price + Greeks (closed-form)
  tasks.py               # heatmap, scenarios, delta-hedge (simulated + real data), plotting
  cli.py                 # argparse CLI entrypoints (CSV + PNG writers)
outputs/                 # sample CSVs (generated or prefilled)
data/                    # (optional) put real price paths here
docs/
  greeks_decisions_brief.md  # one-page "Greeks → Decisions" brief
```

## Testing

Run the automated checks locally before shipping changes:

```bash
python -m pip install -r requirements.txt
pytest
```

## Notes & disclaimers
- Educational sample — not investment advice. Extend with transaction costs, slippage, discrete hedging errors, and real data feeds before making claims.
- Vega is returned per absolute vol point (1.00 = 100 vol points). Convert as needed.
- Theta is annualized; divide by 365 for calendar-day theta if you prefer.
- Feel free to use all resources ! we encourage to share Knowledge ! 
- 
