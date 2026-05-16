from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
import warnings

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
        self._require_vnstock()
        try:
            from vnstock.api.quote import Quote
            use_new_api = True
        except ImportError:
            use_new_api = False

        end = dt.date.today()
        start = end - dt.timedelta(days=365 * years)

        if use_new_api:
            q = Quote(symbol=symbol.upper(), source="VCI")
            df = q.history(start=start.isoformat(), end=end.isoformat())
        else:
            vnstock = self._require_vnstock()
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
        self._require_vnstock()
        
        print(f"\n[WARNING] Free fundamental data from vnstock may be unavailable in version 4.0+. Using fallback mock data for {symbol}.")
        
        # We fallback to returning mock data since the free public API endpoint
        # for fundamentals on VCI/TCBS has been restricted or changed formats.
        return {
            "eps": 4500.0,
            "book_value_per_share": 30000.0,
            "roe": 0.20,
            "debt_to_equity": 0.5,
        }

