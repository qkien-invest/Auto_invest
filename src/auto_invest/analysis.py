from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class StockValuationInput:
    price: float
    eps: float
    growth_rate: float
    discount_rate: float
    terminal_growth: float = 0.03
    years: int = 5


def compute_returns(series: list[float]) -> list[float]:
    """Compute simple returns from a close-price series."""
    if len(series) < 2:
        raise ValueError("need at least 2 price points")

    out: list[float] = []
    for prev, curr in zip(series[:-1], series[1:]):
        if prev == 0:
            continue
        out.append((curr - prev) / prev)
    return out


def stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(var)


def annualized_volatility(returns: list[float], trading_days: int = 252) -> float:
    return stddev(returns) * math.sqrt(trading_days)


def pe_ratio(price: float, eps: float) -> float:
    if eps <= 0:
        raise ValueError("eps must be > 0 for P/E ratio")
    return price / eps


def mean(values: list[float]) -> float:
    return 0.0 if not values else sum(values) / len(values)


def annualized_return(returns: list[float], trading_days: int = 252) -> float:
    """Approximate annualized return from mean daily return."""
    daily = mean(returns)
    return (1 + daily) ** trading_days - 1


def dcf_intrinsic_value(inp: StockValuationInput) -> float:
    """Simple EPS-based DCF intrinsic value estimate."""
    if inp.discount_rate <= inp.terminal_growth:
        raise ValueError("discount_rate must be greater than terminal_growth")
    if inp.years < 1:
        raise ValueError("years must be >= 1")

    pv = 0.0
    cashflow = inp.eps
    for year in range(1, inp.years + 1):
        cashflow *= 1 + inp.growth_rate
        pv += cashflow / ((1 + inp.discount_rate) ** year)

    terminal = cashflow * (1 + inp.terminal_growth) / (inp.discount_rate - inp.terminal_growth)
    pv += terminal / ((1 + inp.discount_rate) ** inp.years)
    return pv


def valuation_summary(inp: StockValuationInput) -> dict:
    intrinsic = dcf_intrinsic_value(inp)
    pe = pe_ratio(inp.price, inp.eps)
    mos = (intrinsic - inp.price) / intrinsic

    return {
        "current_price": inp.price,
        "intrinsic_value": intrinsic,
        "pe_ratio": pe,
        "margin_of_safety": mos,
        "is_undervalued": intrinsic > inp.price,
    }
