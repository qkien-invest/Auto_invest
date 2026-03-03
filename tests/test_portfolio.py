from auto_invest.portfolio import (
    beta_vs_market,
    historical_var,
    inverse_volatility_weights,
    portfolio_report,
)


def test_inverse_volatility_weights_sum_to_one():
    returns = {
        "A": [0.01, -0.02, 0.015, 0.004],
        "B": [0.005, -0.006, 0.007, 0.002],
        "C": [0.02, -0.025, 0.018, -0.004],
    }
    weights = inverse_volatility_weights(returns)
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert all(w > 0 for w in weights.values())


def test_historical_var_positive_loss_number():
    series = [0.02, -0.01, -0.03, 0.01, -0.02]
    var_95 = historical_var(series, confidence=0.95)
    assert var_95 >= 0


def test_beta_vs_market_finite():
    beta = beta_vs_market([0.01, 0.02, -0.01], [0.005, 0.01, -0.004])
    assert isinstance(beta, float)


def test_portfolio_report_contains_return_and_var():
    report = portfolio_report(
        {
            "A": [0.01, -0.02, 0.015, 0.004],
            "B": [0.005, -0.006, 0.007, 0.002],
        },
        market_returns=[0.002, -0.01, 0.008, 0.001],
    )
    assert "portfolio_annual_return" in report
    assert "portfolio_var" in report
    assert "portfolio_beta_vs_market" in report
