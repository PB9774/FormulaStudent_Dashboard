# Accelerons Electric — BMS Monitor

A fully industrial-grade **PyQt6 vehicle dashboard** for Battery Management System telemetry.

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install PyQt6 pyqtgraph numpy

# 2. Run
python main.py
```

---

## 📐 Project Architecture

```
accelerons_bms/
├── main.py                         # Entry point
├── requirements.txt
│
├── core/                           # Business logic (no UI imports)
│   ├── data_engine.py              # 10 Hz BMS simulator / UART adapter
│   └── logger.py                   # CSV session logger
│
├── ui/
│   ├── main_window.py              # QMainWindow + QTimer + QStackedWidget
│   ├── styles/
│   │   └── theme.py                # All colours, fonts, and master QSS
│   ├── widgets/
│   │   ├── circular_gauge.py       # Custom QPainter glass-effect gauge
│   │   └── nav_bar.py              # Bottom navigation bar
│   └── pages/
│       ├── dashboard_page.py       # Screen 1 — SOC, speed, modules, ΔV
│       ├── heatmap_page.py         # Screen 2 — Cell voltage heatmap
│       ├── analytics_page.py       # Screen 3 — Live pyqtgraph charts
│       └── storage_page.py         # Screen 4 — CSV log file explorer
│
└── logs/                           # Auto-created, holds saved CSV files
```

---

## 🖥️ Screens

| # | Screen      | Key Features |
|---|-------------|-------------|
| 1 | Dashboard   | Glass SOC gauge · Speed readout · 7 module bars · ΔV alert · Save Logs |
| 2 | Heatmap     | 7 × 14 cell grid · Green/Amber/Red voltage status · Scrollable |
| 3 | Analytics   | Live Current / SOC / Temp graphs · 1m–30m range selector |
| 4 | Storage     | CSV log explorer · File size & timestamp · Open in Finder/Explorer |

---

## 🔌 Connecting Real UART / CAN Data

Replace the `_simulate()` method in `core/data_engine.py` with your serial/CAN read:

```python
import serial

class DataEngine:
    def __init__(self):
        self._ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.09)

    def _simulate(self):
        # Parse your UART frame here and populate self._modules, self._speed etc.
        raw = self._ser.readline().decode().strip()
        # ... parse raw ...
```

All UI will work unchanged because it reads only from properties.

---

## 🏎️ Design System

| Token         | Value      | Usage |
|---------------|-----------|-------|
| Neon Green    | `#39FF14` | Normal state, brand accents |
| Amber         | `#FFB300` | Warning, speed, temperature |
| Red           | `#FF3535` | Critical / high voltage |
| Accent Blue   | `#4A9EFF` | Pack voltage, download buttons |
| BG Base       | `#0B0D12` | App background |

Font: **Roboto / Inter** — display; **Roboto Mono** — numeric readouts

---

## ⚙️ Performance

- **10 Hz** update rate via 100 ms `QTimer`
- Analytics history stored in `deque(maxlen=18_000)` — 30 min at 10 Hz, zero memory leak
- Only the **active page** is refreshed each tick — inactive pages skip update
- `pyqtgraph` renders with hardware-accelerated OpenGL

---

*Accelerons Electric Racing — BMS Monitor v1.0*
Author - Piyush Bansal
