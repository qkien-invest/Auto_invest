from __future__ import annotations

import csv
import datetime as dt
import io
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class MarketDataCollector:
    """Collect stock and market index prices from Stooq CSV endpoint."""

    base_url: str = "https://stooq.com/q/d/l/"
    market_symbol: str = "^spx"

    def fetch_symbol_history(self, symbol: str) -> list[dict[str, str]]:
        """Fetch historical OHLCV rows for one symbol from Stooq."""
        query = f"{self.base_url}?s={symbol.lower()}&i=d"
        with urllib.request.urlopen(query, timeout=20) as response:
            payload = response.read().decode("utf-8")

        rows = list(csv.DictReader(io.StringIO(payload)))
        if not rows or rows[0].get("Date") in (None, ""):
            raise RuntimeError(f"No data returned for symbol: {symbol}")
        return rows

    def fetch_prices(
        self,
        symbols: Iterable[str],
        include_market: bool = True,
    ) -> dict[str, list[tuple[dt.date, float]]]:
        """Fetch daily close prices for symbols (and optionally market index)."""
        normalized = [s.lower() for s in symbols]
        if include_market and self.market_symbol.lower() not in normalized:
            normalized.append(self.market_symbol.lower())

        if not normalized:
            raise ValueError("symbols must not be empty")

        out: dict[str, list[tuple[dt.date, float]]] = {}
        for symbol in normalized:
            history = self.fetch_symbol_history(symbol)
            points: list[tuple[dt.date, float]] = []
            for row in history:
                close = row.get("Close")
                day = row.get("Date")
                if not close or close in ("", "0") or not day:
                    continue
                points.append((dt.date.fromisoformat(day), float(close)))
            points.sort(key=lambda x: x[0])
            out[symbol] = points

        return out

    @staticmethod
    def save_prices(prices: dict[str, list[tuple[dt.date, float]]], output_path: str) -> None:
        """Save merged close prices to CSV."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        dates = sorted({d for values in prices.values() for d, _ in values})
        symbols = sorted(prices.keys())
        lookup = {symbol: {day: close for day, close in series} for symbol, series in prices.items()}

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", *symbols])
            for day in dates:
                writer.writerow([day.isoformat(), *[lookup[s].get(day, "") for s in symbols]])

    @staticmethod
    def load_prices(path: str) -> dict[str, list[tuple[dt.date, float]]]:
        """Load merged price CSV created by save_prices."""
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("price file has no header")

            symbols = [name for name in reader.fieldnames if name != "date"]
            out: dict[str, list[tuple[dt.date, float]]] = {s: [] for s in symbols}

            for row in reader:
                day = dt.date.fromisoformat(row["date"])
                for symbol in symbols:
                    value = row[symbol]
                    if value != "":
                        out[symbol].append((day, float(value)))
        return out
