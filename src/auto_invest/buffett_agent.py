from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BuffettAgentInput:
    symbol: str
    current_price: float
    eps: float
    book_value_per_share: float
    roe: float
    debt_to_equity: float


class BuffettStyleAgent:
    """Simple rule-based agent inspired by Warren Buffett style."""

    def evaluate(self, data: BuffettAgentInput) -> dict:
        pe = data.current_price / data.eps if data.eps > 0 else float("inf")
        pb = data.current_price / data.book_value_per_share if data.book_value_per_share > 0 else float("inf")

        checks = {
            "profitable_eps": data.eps > 0,
            "reasonable_pe": pe <= 15,
            "reasonable_pb": pb <= 1.5,
            "high_roe": data.roe >= 0.15,
            "low_debt": data.debt_to_equity <= 1.0,
        }

        passed = sum(checks.values())
        if passed >= 4:
            rating = "BUY"
        elif passed >= 3:
            rating = "HOLD"
        else:
            rating = "PASS"

        return {
            "symbol": data.symbol,
            "rating": rating,
            "score": passed,
            "max_score": len(checks),
            "metrics": {
                "current_price": data.current_price,
                "eps": data.eps,
                "pe": pe,
                "book_value_per_share": data.book_value_per_share,
                "pb": pb,
                "roe": data.roe,
                "debt_to_equity": data.debt_to_equity,
            },
            "checks": checks,
            "notes": [
                "Rule-based educational model, not investment advice.",
                "Uses simplified Buffett-style heuristics.",
            ],
        }
