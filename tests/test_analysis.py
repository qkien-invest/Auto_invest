import math

from auto_invest.analysis import (
    StockValuationInput,
    annualized_return,
    dcf_intrinsic_value,
    pe_ratio,
)


def test_pe_ratio():
    assert pe_ratio(100, 5) == 20


def test_dcf_intrinsic_value_positive():
    inp = StockValuationInput(
        price=100,
        eps=5,
        growth_rate=0.1,
        discount_rate=0.12,
        terminal_growth=0.03,
        years=5,
    )
    intrinsic = dcf_intrinsic_value(inp)
    assert intrinsic > 0
    assert math.isfinite(intrinsic)


def test_annualized_return_positive_for_positive_daily_mean():
    r = annualized_return([0.001, 0.002, 0.0, 0.001])
    assert r > 0
