import math

import pytest

from greeks_engine import bsm


def test_greeks_match_reference_values():
    """Anchor the BSM implementation to a known reference quote."""
    result = bsm.greeks(S=100, K=100, T=1.0, r=0.05, q=0.01, sigma=0.20, kind="call")

    assert result["price"] == pytest.approx(9.8262977827, rel=1e-9)
    assert result["delta"] == pytest.approx(0.6117631008, rel=1e-9)
    assert result["gamma"] == pytest.approx(0.01887964716, rel=1e-9)
    assert result["vega"] == pytest.approx(37.759294329, rel=1e-9)
    assert result["theta"] == pytest.approx(-5.731666947, rel=1e-9)
    assert result["rho"] == pytest.approx(51.350012298, rel=1e-9)


def test_d1_d2_returns_nan_for_invalid_params():
    d1, d2 = bsm.d1_d2(S=0, K=100, T=1, r=0.05, q=0.0, sigma=0.2)
    assert math.isnan(d1)
    assert math.isnan(d2)
