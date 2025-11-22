import argparse, os
from .tasks import delta_heatmap, delta_hedge_example, plot_delta_heatmap, scenario_table

def main():
    p = argparse.ArgumentParser(prog="greeks-engine", description="Options Greeks & Delta-Hedge Engine — Python (BSM)")
    sub = p.add_subparsers(dest="cmd", required=True)

    hp = sub.add_parser("heatmap", help="Generate Delta heatmap across moneyness × tenor")
    hp.add_argument("--S", type=float, default=20000.0)
    hp.add_argument("--r", type=float, default=0.06)
    hp.add_argument("--q", type=float, default=0.01)
    hp.add_argument("--sigma", type=float, default=0.20)
    hp.add_argument("--m-start", type=float, default=0.8)
    hp.add_argument("--m-end", type=float, default=1.2)
    hp.add_argument("--m-steps", type=int, default=9)
    hp.add_argument("--t-start", type=float, default=0.1)
    hp.add_argument("--t-end", type=float, default=1.0)
    hp.add_argument("--t-steps", type=int, default=10)
    hp.add_argument("--out", type=str, default="outputs/delta_heatmap.csv")
    hp.add_argument("--png-out", type=str, default="outputs/delta_heatmap.png")

    sp = sub.add_parser("scenarios", help="Generate scenario table (±vol, ±rate) at ATM")
    sp.add_argument("--S", type=float, default=20000.0)
    sp.add_argument("--K", type=float, default=20000.0)
    sp.add_argument("--T", type=float, default=0.25)
    sp.add_argument("--q", type=float, default=0.01)
    sp.add_argument("--sigmas", type=float, nargs="+", default=[0.15, 0.20, 0.25])
    sp.add_argument("--rates", type=float, nargs="+", default=[0.05, 0.06, 0.07])
    sp.add_argument("--out", type=str, default="outputs/scenario_table.csv")

    dp = sub.add_parser("hedge", help="Run a simple rolling delta-hedge toy example")
    dp.add_argument("--days", type=int, default=60)
    dp.add_argument("--S", type=float, default=20000.0)
    dp.add_argument("--K", type=float, default=20000.0)
    dp.add_argument("--T", type=float, default=0.25)
    dp.add_argument("--r", type=float, default=0.06)
    dp.add_argument("--q", type=float, default=0.01)
    dp.add_argument("--sigma", type=float, default=0.20)
    dp.add_argument("--seed", type=int, default=42)
    dp.add_argument("--data", type=str, help="Path to CSV with real underlying prices (e.g., NIFTY closes)")
    dp.add_argument("--price-col", type=str, default="Close")
    dp.add_argument("--date-col", type=str, default="Date")
    dp.add_argument("--out", type=str, default="outputs/delta_hedge_example.csv")

    args = p.parse_args()

    if args.cmd == "heatmap":
        df = delta_heatmap(S0=args.S, r=args.r, q=args.q, sigma=args.sigma,
                           m_start=args.m_start, m_end=args.m_end, m_steps=args.m_steps,
                           t_start=args.t_start, t_end=args.t_end, t_steps=args.t_steps)
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        df.to_csv(args.out)
        if args.png_out:
            plot_delta_heatmap(df, png_path=args.png_out)
        print(f"Wrote {args.out}")
    elif args.cmd == "scenarios":
        df = scenario_table(S0=args.S, K_atm=args.K, T=args.T, q=args.q,
                            sigmas=tuple(args.sigmas), rates=tuple(args.rates))
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        df.to_csv(args.out, index=False)
        print(f"Wrote {args.out}")
    elif args.cmd == "hedge":
        df = delta_hedge_example(days=args.days, S0=args.S, K_atm=args.K, T=args.T, r=args.r, q=args.q, sigma=args.sigma, seed=args.seed, data_path=args.data, price_col=args.price_col, date_col=args.date_col)
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        df.to_csv(args.out, index=False)
        print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
