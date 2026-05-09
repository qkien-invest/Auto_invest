# Auto Invest Toolkit (Simplified Buffett Agent)

Dự án Python giúp **phân tích cổ phiếu tự động** theo hướng đơn giản giống `ai-hedge-fund`, nhưng chỉ dùng **1 agent kiểu Warren Buffett** và dữ liệu free từ **vnstock**.

## Tính năng chính

- Agent rule-based kiểu Buffett:
  - EPS > 0
  - P/E <= 15
  - P/B <= 1.5
  - ROE >= 15%
  - Debt/Equity <= 1.0
- Lấy dữ liệu giá + cơ bản từ `vnstock`.
- CLI đơn giản để chạy phân tích 1 mã.

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Chạy agent Buffett

### Dùng dữ liệu fundamentals tự động từ vnstock

```bash
PYTHONPATH=src python -m auto_invest.main buffett --symbol FPT
```

### Hoặc truyền tay fundamentals

```bash
PYTHONPATH=src python -m auto_invest.main buffett \
  --symbol FPT \
  --eps 4500 \
  --book-value-per-share 30000 \
  --roe 0.22 \
  --debt-to-equity 0.35
```

## Lưu ý

- Đây là công cụ học tập/nghiên cứu, **không phải khuyến nghị đầu tư**.
- Nên kiểm tra lại dữ liệu thực tế trước khi ra quyết định.
