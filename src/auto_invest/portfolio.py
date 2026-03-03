from __future__ import annotations

from auto_invest.analysis import annualized_return, annualized_volatility, mean, stddev


def historical_var(returns: list[float], confidence: float = 0.95) -> float:
    """Historical VaR as a positive loss number."""
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if not returns:
        raise ValueError("returns must not be empty")

    sorted_r = sorted(returns)
    idx = int((1 - confidence) * (len(sorted_r) - 1))
    return max(0.0, -sorted_r[idx])


def covariance(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    mx = mean(x)
    my = mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) - 1)


def correlation_matrix(returns_by_asset: dict[str, list[float]]) -> dict[str, dict[str, float]]:
    assets = list(returns_by_asset.keys())
    matrix: dict[str, dict[str, float]] = {a: {} for a in assets}

    for a in assets:
        for b in assets:
            xa = returns_by_asset[a]
            xb = returns_by_asset[b]
            sa = stddev(xa)
            sb = stddev(xb)
            cov = covariance(xa, xb)
            matrix[a][b] = 0.0 if sa == 0 or sb == 0 else cov / (sa * sb)
    return matrix


def inverse_volatility_weights(returns_by_asset: dict[str, list[float]]) -> dict[str, float]:
    if not returns_by_asset:
        raise ValueError("returns_by_asset must not be empty")

    vols = {asset: stddev(values) for asset, values in returns_by_asset.items()}
    if any(v <= 0 for v in vols.values()):
        raise ValueError("all assets must have positive volatility")

    inv = {asset: 1 / v for asset, v in vols.items()}
    total = sum(inv.values())
    return {asset: value / total for asset, value in inv.items()}


def beta_vs_market(asset_returns: list[float], market_returns: list[float]) -> float:
    """Estimate beta = cov(asset, market)/var(market)."""
    cov = covariance(asset_returns, market_returns)
    var_mkt = covariance(market_returns, market_returns)
    return 0.0 if var_mkt == 0 else cov / var_mkt


def portfolio_report(
    returns_by_asset: dict[str, list[float]],
    confidence: float = 0.95,
    market_returns: list[float] | None = None,
) -> dict:
    weights = inverse_volatility_weights(returns_by_asset)
    n = min(len(v) for v in returns_by_asset.values())
    portfolio_returns = [sum(weights[a] * returns_by_asset[a][i] for a in returns_by_asset) for i in range(n)]

    report = {
        "weights": weights,
        "portfolio_annual_return": annualized_return(portfolio_returns),
        "portfolio_volatility": annualized_volatility(portfolio_returns),
        "portfolio_var": historical_var(portfolio_returns, confidence),
        "correlation": correlation_matrix(returns_by_asset),
    }

    if market_returns is not None and len(market_returns) >= n:
        trimmed_market = market_returns[:n]
        report["portfolio_beta_vs_market"] = beta_vs_market(portfolio_returns, trimmed_market)

    return report
