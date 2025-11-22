import math

import pytest

from greeks_engine.bsm import d1_d2, greeks, norm_cdf, price


def test_price_matches_reference_call_put():
    call_price = price(100, 100, 1.0, 0.05, 0.0, 0.2, "call")
    put_price = price(100, 100, 1.0, 0.05, 0.0, 0.2, "put")

    assert call_price == pytest.approx(10.4506, rel=1e-4)
    assert put_price == pytest.approx(5.5735, rel=1e-4)


def test_greeks_match_reference_values():
    g = greeks(100, 100, 1.0, 0.05, 0.0, 0.2, "call")

    assert g["delta"] == pytest.approx(0.63683, rel=1e-4)
    assert g["gamma"] == pytest.approx(0.018762, rel=1e-4)
    assert g["vega"] == pytest.approx(37.524, rel=1e-4)
    assert g["rho"] == pytest.approx(53.2325, rel=1e-4)
    assert g["theta"] == pytest.approx(-6.4140, rel=1e-4)


def test_d1_d2_nan_when_invalid_inputs():
    d1, d2 = d1_d2(-1.0, 100, 1.0, 0.05, 0.0, 0.2)
    assert math.isnan(d1) and math.isnan(d2)


def test_norm_cdf_monotonicity():
    assert norm_cdf(-1.0) < norm_cdf(0.0) < norm_cdf(1.0)
