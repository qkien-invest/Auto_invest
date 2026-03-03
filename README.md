# Auto Invest Toolkit

Toolkit Python giúp **tự động hóa quy trình đầu tư cổ phiếu** theo 3 bước:

1. **Thu thập dữ liệu** cổ phiếu + chỉ số thị trường.
2. **Phân tích & định giá** cổ phiếu (P/E + DCF đơn giản).
3. **Đánh giá rủi ro & phân bổ danh mục** (volatility, VaR, tương quan, inverse-volatility).

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

> Nếu môi trường bị chặn mạng/proxy, bạn vẫn có thể chạy test bằng `PYTHONPATH=src pytest -q`.

## Cách dùng CLI

### 1) Thu thập dữ liệu

```bash
PYTHONPATH=src python -m auto_invest.main fetch \
  --symbols aapl.us msft.us nvda.us \
  --market-symbol ^spx \
  --output data/prices.csv
```

### 2) Phân tích và định giá

```bash
PYTHONPATH=src python -m auto_invest.main analyze \
  --price-file data/prices.csv \
  --symbol aapl.us \
  --eps 6.43 \
  --growth 0.12 \
  --discount-rate 0.1 \
  --terminal-growth 0.03 \
  --years 5
```

### 3) Tối ưu danh mục và rủi ro

```bash
PYTHONPATH=src python -m auto_invest.main optimize \
  --price-file data/prices.csv \
  --market-symbol ^spx \
  --var-confidence 0.95
```

## Thiết kế

- `src/auto_invest/data_collector.py`
  - Lấy dữ liệu lịch sử từ Stooq cho nhiều mã.
  - Tự động gộp thêm market symbol (mặc định `^spx`).
  - Lưu/đọc CSV hợp nhất.
- `src/auto_invest/analysis.py`
  - Tính returns, volatility, annualized return.
  - P/E và DCF định giá nội tại.
- `src/auto_invest/portfolio.py`
  - Historical VaR, correlation matrix.
  - Inverse-volatility allocation.
  - Ước tính beta danh mục so với market (nếu có dữ liệu market).
- `src/auto_invest/main.py`
  - CLI cho `fetch`, `analyze`, `optimize`.
  - Căn chỉnh dữ liệu theo **ngày giao dịch chung** trước khi tối ưu.

## Lưu ý

- Đây là công cụ hỗ trợ học tập/nghiên cứu, **không phải khuyến nghị đầu tư**.
- Dữ liệu giá dùng nguồn công khai Stooq.
