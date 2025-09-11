import math

def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def d1_d2(S, K, T, r, q, sigma):
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return float("nan"), float("nan")
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2

def price(S, K, T, r, q, sigma, kind="call"):
    d1, d2 = d1_d2(S, K, T, r, q, sigma)
    if kind == "call":
        return S * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    else:
        return K * math.exp(-r * T) * norm_cdf(-d2) - S * math.exp(-q * T) * norm_cdf(-d1)

def greeks(S, K, T, r, q, sigma, kind="call"):
    d1, d2 = d1_d2(S, K, T, r, q, sigma)
    n_prime = math.exp(-0.5 * d1**2) / math.sqrt(2*math.pi) if not math.isnan(d1) else float("nan")
    disc_q = math.exp(-q*T)
    disc_r = math.exp(-r*T)

    delta = disc_q * norm_cdf(d1) if kind == "call" else disc_q * (norm_cdf(d1) - 1.0)
    gamma = disc_q * n_prime / (S * sigma * math.sqrt(T)) if T > 0 and sigma > 0 else float("nan")
    vega  = S * disc_q * n_prime * math.sqrt(T)  # per 1.0 vol
    theta = (-S * disc_q * n_prime * sigma / (2*math.sqrt(T))
             - (r * K * disc_r * norm_cdf(d2) if kind == "call" else -r * K * disc_r * norm_cdf(-d2))
             + (q * S * disc_q * norm_cdf(d1) if kind == "call" else q * S * disc_q * norm_cdf(-d1)))
    rho = (K * T * disc_r * norm_cdf(d2) if kind == "call" else -K * T * disc_r * norm_cdf(-d2))
    return {"price": price(S, K, T, r, q, sigma, kind),
            "delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}
