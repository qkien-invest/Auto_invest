from auto_invest.vnstock_data import VnStockDataCollector


def test_require_vnstock_raises_when_not_installed(monkeypatch):
    import builtins

    collector = VnStockDataCollector()
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "vnstock":
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        collector._require_vnstock()
        assert False, "Expected ImportError"
    except ImportError as exc:
        assert "pip install vnstock" in str(exc)
