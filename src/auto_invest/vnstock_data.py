from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass
class VnStockDataCollector:
    """Fetch VN stock prices/fundamentals from vnstock (free data)."""

    source: str = "vnstock"

    def _require_vnstock(self):
        try:
            import vnstock  # type: ignore

            return vnstock
        except ImportError as exc:
            raise ImportError(
                "vnstock chưa được cài đặt. Hãy chạy: pip install vnstock"
            ) from exc

    def fetch_price_history(self, symbol: str, years: int = 3) -> list[tuple[dt.date, float]]:
        vnstock = self._require_vnstock()

        end = dt.date.today()
        start = end - dt.timedelta(days=365 * years)
        df = vnstock.stock_historical_data(
            symbol=symbol.upper(),
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            resolution="1D",
            type="stock",
            beautify=False,
            decor=False,
            source="VCI",
        )
        if df is None or len(df) == 0:
            raise RuntimeError(f"No historical data for symbol: {symbol}")

        out: list[tuple[dt.date, float]] = []
        for _, row in df.iterrows():
            day = row["time"]
            close = row["close"]
            day_value = day.date() if hasattr(day, "date") else dt.date.fromisoformat(str(day)[:10])
            out.append((day_value, float(close)))
        return out

    def fetch_fundamentals(self, symbol: str) -> dict[str, float]:
        vnstock = self._require_vnstock()
        overview = vnstock.company_overview(symbol.upper())
        if overview is None or len(overview) == 0:
            raise RuntimeError(f"No fundamental data for symbol: {symbol}")

        row = overview.iloc[0]
        return {
            "eps": float(row.get("eps", 0.0) or 0.0),
            "book_value_per_share": float(row.get("bookValue", 0.0) or 0.0),
            "roe": float(row.get("roe", 0.0) or 0.0),
            "debt_to_equity": float(row.get("debtEquity", 0.0) or 0.0),
        }
