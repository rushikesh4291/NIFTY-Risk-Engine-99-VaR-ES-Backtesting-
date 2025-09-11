# Greeks → Decisions (One-Pager)

**Instrument:** NIFTY ATM Call | **S₀:** 20000 | **K:** 20000 | **T:** 0.25y | **r:** 6.00% | **q:** 1.00% | **σ:** 20%

## Quick Reads
- **Delta heatmap:** see `outputs/delta_heatmap.csv`.
- **Scenario table:** see `outputs/scenario_table.csv`.
- **Delta-hedge example:** see `outputs/delta_hedge_example.csv`.

## How to use
- Use **Delta** to size hedge ratios; watch **Gamma** near ATM (rebalance more often).
- **Vega** = vol sensitivity; offset with opposite-vega or express a vol view.
- **Theta** = time decay; short-dated options decay fastest.
- **Rho** = rate sensitivity; relevant if rates shift materially.

> Swap the toy path with real NIFTY prices; keep the CSV interfaces intact.
