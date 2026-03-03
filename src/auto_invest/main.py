from __future__ import annotations

import argparse
import json

from auto_invest.analysis import StockValuationInput, compute_returns, valuation_summary
from auto_invest.data_collector import MarketDataCollector
from auto_invest.portfolio import portfolio_report


def _align_prices_to_common_dates(price_map: dict[str, list[tuple]]) -> dict[str, list[float]]:
    """Align symbols to common trading dates and return close arrays."""
    by_symbol = {
        s: {d: p for d, p in series}
        for s, series in price_map.items()
        if series
    }
    common_dates = None
    for values in by_symbol.values():
        dates = set(values.keys())
        common_dates = dates if common_dates is None else common_dates & dates

    if not common_dates:
        raise ValueError("No common trading dates among symbols")

    ordered = sorted(common_dates)
    return {s: [lookup[d] for d in ordered] for s, lookup in by_symbol.items()}


def cmd_fetch(args: argparse.Namespace) -> None:
    collector = MarketDataCollector(market_symbol=args.market_symbol)
    prices = collector.fetch_prices(args.symbols, include_market=not args.no_market)
    collector.save_prices(prices, args.output)
    print(f"Saved price data to {args.output}")


def cmd_analyze(args: argparse.Namespace) -> None:
    collector = MarketDataCollector()
    price_map = collector.load_prices(args.price_file)

    if args.symbol not in price_map or not price_map[args.symbol]:
        raise ValueError(f"Symbol '{args.symbol}' not found in price file")

    latest_price = price_map[args.symbol][-1][1]
    summary = valuation_summary(
        StockValuationInput(
            price=latest_price,
            eps=args.eps,
            growth_rate=args.growth,
            discount_rate=args.discount_rate,
            terminal_growth=args.terminal_growth,
            years=args.years,
        )
    )
    print(json.dumps(summary, indent=2))


def cmd_optimize(args: argparse.Namespace) -> None:
    collector = MarketDataCollector(market_symbol=args.market_symbol)
    price_map = collector.load_prices(args.price_file)

    aligned_prices = _align_prices_to_common_dates(price_map)
    returns_by_symbol = {
        symbol: compute_returns(prices)
        for symbol, prices in aligned_prices.items()
        if len(prices) >= 2
    }

    market_returns = None
    if args.market_symbol in returns_by_symbol:
        market_returns = returns_by_symbol[args.market_symbol]
        returns_by_symbol = {
            s: r for s, r in returns_by_symbol.items() if s != args.market_symbol
        }

    if not returns_by_symbol:
        raise ValueError("No investable symbols found after excluding market symbol")

    report = portfolio_report(
        returns_by_symbol,
        confidence=args.var_confidence,
        market_returns=market_returns,
    )
    print(json.dumps(report, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auto Invest Toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch market data")
    p_fetch.add_argument("--symbols", nargs="+", required=True, help="Stooq symbols, e.g. aapl.us")
    p_fetch.add_argument("--market-symbol", default="^spx")
    p_fetch.add_argument("--no-market", action="store_true", help="Do not auto-append market symbol")
    p_fetch.add_argument("--output", default="data/prices.csv")
    p_fetch.set_defaults(func=cmd_fetch)

    p_analyze = sub.add_parser("analyze", help="Analyze and value a stock")
    p_analyze.add_argument("--price-file", required=True)
    p_analyze.add_argument("--symbol", required=True)
    p_analyze.add_argument("--eps", type=float, required=True)
    p_analyze.add_argument("--growth", type=float, required=True)
    p_analyze.add_argument("--discount-rate", type=float, required=True)
    p_analyze.add_argument("--terminal-growth", type=float, default=0.03)
    p_analyze.add_argument("--years", type=int, default=5)
    p_analyze.set_defaults(func=cmd_analyze)

    p_opt = sub.add_parser("optimize", help="Risk and portfolio allocation")
    p_opt.add_argument("--price-file", required=True)
    p_opt.add_argument("--market-symbol", default="^spx")
    p_opt.add_argument("--var-confidence", type=float, default=0.95)
    p_opt.set_defaults(func=cmd_optimize)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
