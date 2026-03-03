import datetime as dt

from auto_invest.main import _align_prices_to_common_dates


def test_align_prices_to_common_dates():
    price_map = {
        "a": [(dt.date(2024, 1, 1), 10.0), (dt.date(2024, 1, 2), 11.0)],
        "b": [(dt.date(2024, 1, 2), 20.0), (dt.date(2024, 1, 3), 21.0)],
    }
    aligned = _align_prices_to_common_dates(price_map)
    assert aligned == {"a": [11.0], "b": [20.0]}
