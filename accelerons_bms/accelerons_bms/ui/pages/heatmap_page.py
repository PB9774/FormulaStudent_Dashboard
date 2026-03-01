"""
ui/pages/heatmap_page.py  [BIGGER FONTS + TELEMETRY STRIP]
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Cell Heatmap Page (Screen 2)
• Bigger label fonts throughout
• TelemetryStrip at top showing SOC + Speed
• Two segment cards per row
"""

from __future__ import annotations
import random

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy, QProgressBar,
    QGridLayout,
)

from ui.styles.theme           import Color, Font
from ui.widgets.telemetry_strip import TelemetryStrip
from core.data_engine           import DataEngine

_V_LOW  = 3.40
_V_HIGH = 4.10
_V_MIN  = 3.00
_V_MAX  = 4.20
NTC_COUNT = 7


def _bar_color(v: float) -> str:
    if v < _V_LOW or v > _V_HIGH: return Color.RED_BAR
    if v < 3.70:                   return Color.AMBER_BAR
    return Color.GREEN_BAR


# ── Cell bar ──────────────────────────────────────────────────────────────────

class _CellBar(QWidget):
    def __init__(self, cell_idx: int, parent=None) -> None:
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self._badge = QLabel(f"C{cell_idx + 1}")
        self._badge.setFixedSize(24, 24)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setStyleSheet(
            f"background:{Color.BG_BASE}; border:1.5px solid {Color.BORDER_SEG};"
            f"border-radius:12px; color:{Color.ACCENT_BLUE};"
            f"font-size:{Font.SIZE_SM}px; font-weight:800;"    # SIZE_SM = 11px
        )

        self._bar = QProgressBar()
        self._bar.setRange(0, 1000)
        self._bar.setFixedHeight(24)
        self._bar.setTextVisible(True)
        self._bar.setFormat("--- V")
        self._bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:5px;"
            f"color:{Color.WHITE};font-family:{Font.MONO};"
            f"font-size:{Font.SIZE_SM}px;font-weight:700;text-align:center;}}"
            f"QProgressBar::chunk{{border-radius:5px;background:{Color.GREEN_BAR};}}"
        )

        lay.addWidget(self._badge)
        lay.addWidget(self._bar)

    def refresh(self, voltage: float) -> None:
        frac = max(0.0, min(1.0, (voltage - _V_MIN) / (_V_MAX - _V_MIN)))
        self._bar.setValue(int(frac * 1000))
        fill = _bar_color(voltage)
        self._bar.setFormat(f"{voltage:.2f} V")
        self._bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:5px;"
            f"color:{Color.WHITE};font-family:{Font.MONO};"
            f"font-size:{Font.SIZE_SM}px;font-weight:700;text-align:center;}}"
            f"QProgressBar::chunk{{border-radius:5px;background:{fill};}}"
        )


# ── NTC pill ──────────────────────────────────────────────────────────────────

class _NtcPill(QLabel):
    def __init__(self, ntc_idx: int, parent=None) -> None:
        super().__init__(parent)
        self._ntc_idx = ntc_idx
        self.setFixedHeight(24)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(72)
        self._set(25.0)

    def _set(self, temp: float) -> None:
        self.setText(f"T{self._ntc_idx+1}: {temp:.1f}°C")
        if temp > 50:   bg, fg = Color.RED_DIM,   Color.RED
        elif temp > 40: bg, fg = Color.AMBER_DIM,  Color.AMBER
        else:           bg, fg = Color.BG_PANEL,   Color.TEXT_SEC
        self.setStyleSheet(
            f"background:{bg}; color:{fg}; border:1px solid {Color.BORDER};"
            f"border-radius:8px; padding:0 5px; font-family:{Font.MONO};"
            f"font-size:{Font.SIZE_SM}px; font-weight:700;"    # SIZE_SM = 11px
        )

    def refresh(self, temp: float) -> None:
        self._set(temp)


# ── Segment card ──────────────────────────────────────────────────────────────

class _SegmentCard(QFrame):
    CELLS = 14

    def __init__(self, seg_idx: int, engine: DataEngine, parent=None) -> None:
        super().__init__(parent)
        self._idx    = seg_idx
        self._engine = engine
        self._cell_bars: list[_CellBar]  = []
        self._ntc_pills: list[_NtcPill] = []
        self.setObjectName("card_seg")
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 7, 8, 8)
        root.setSpacing(5)

        # Title
        title_frame = QFrame()
        title_frame.setObjectName("card")
        title_frame.setFixedHeight(30)
        t_lay = QHBoxLayout(title_frame)
        t_lay.setContentsMargins(10, 0, 10, 0)
        seg_lbl = QLabel(f"SEGMENT  {self._idx + 1}")
        seg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        seg_lbl.setStyleSheet(
            f"color:{Color.ACCENT_BLUE}; font-size:{Font.SIZE_MD}px; "   # SIZE_MD = 13px
            f"font-weight:800; letter-spacing:3px; background:transparent; border:none;"
        )
        t_lay.addWidget(seg_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title_frame)

        # Cell voltages
        root.addWidget(self._section_hdr("CELL VOLTAGES"))
        grid_w = QWidget()
        grid   = QGridLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)
        for i in range(self.CELLS):
            bar = _CellBar(i)
            self._cell_bars.append(bar)
            grid.addWidget(bar, i // 2, i % 2)
        root.addWidget(grid_w)

        # NTC temps
        root.addWidget(self._section_hdr("NTC TEMPS"))
        ntc_row = QWidget()
        ntc_lay = QHBoxLayout(ntc_row)
        ntc_lay.setContentsMargins(0, 0, 0, 0)
        ntc_lay.setSpacing(4)
        for i in range(NTC_COUNT):
            pill = _NtcPill(i)
            self._ntc_pills.append(pill)
            ntc_lay.addWidget(pill)
        ntc_lay.addStretch()
        root.addWidget(ntc_row)

    def _section_hdr(self, text: str) -> QFrame:
        frame = QFrame()
        frame.setFixedHeight(22)
        frame.setStyleSheet(
            f"background:{Color.BG_CARD2}; border:1px solid {Color.BORDER}; border-radius:5px;"
        )
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(10, 0, 10, 0)
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_SM}px; "  # SIZE_SM = 11px
            f"font-weight:700; letter-spacing:2px; background:transparent; border:none;"
        )
        lay.addWidget(lbl)
        lay.addStretch()
        return frame

    def refresh(self) -> None:
        module = self._engine.modules[self._idx]
        avg_t  = self._engine.module_avg_temp(self._idx)
        for i, cell in enumerate(module.cells):
            self._cell_bars[i].refresh(cell.voltage)
        for i, pill in enumerate(self._ntc_pills):
            pill.refresh(avg_t + (i - 3) * 1.8 + random.gauss(0, 0.2))


# ── Heatmap page ──────────────────────────────────────────────────────────────

class HeatmapPage(QWidget):
    def __init__(self, engine: DataEngine, parent=None) -> None:
        super().__init__(parent)
        self._engine    = engine
        self._segments: list[_SegmentCard] = []
        self._strip = TelemetryStrip()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(6)

        # Telemetry strip at top
        root.addWidget(self._strip)

        # Page header
        root.addWidget(self._build_header())
        root.addWidget(self._build_legend())

        # Scrollable two-column segment list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(8)

        num_segs = DataEngine.NUM_MODULES
        for row_start in range(0, num_segs, 2):
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(8)
            for seg_idx in range(row_start, min(row_start + 2, num_segs)):
                card = _SegmentCard(seg_idx, self._engine)
                self._segments.append(card)
                row_l.addWidget(card, 1)
            if row_start + 1 >= num_segs:
                row_l.addStretch(1)
            c_lay.addWidget(row_w)

        c_lay.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

    def _build_header(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)

        title = QLabel("CELL  HEATMAP")
        title.setObjectName("page_header")

        info = QLabel(
            f"{DataEngine.NUM_MODULES} segs  ·  "
            f"{DataEngine.NUM_MODULES * DataEngine.CELLS_PER_MODULE} cells  ·  "
            f"{DataEngine.NUM_MODULES * NTC_COUNT} NTCs"
        )
        info.setStyleSheet(f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_SM}px;")
        lay.addWidget(title)
        lay.addStretch()
        lay.addWidget(info)
        return w

    def _build_legend(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        for label, color in [
            ("Normal  3.70–4.10 V",     Color.NEON_GREEN),
            ("Low  3.40–3.70 V",         Color.AMBER),
            ("Critical  <3.40 / >4.10", Color.RED),
        ]:
            dot = QLabel("■")
            dot.setStyleSheet(f"color:{color}; font-size:12px;")
            txt = QLabel(label)
            txt.setStyleSheet(f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_SM}px;")
            lay.addWidget(dot)
            lay.addWidget(txt)
        lay.addStretch()
        return w

    def refresh(self, engine: DataEngine) -> None:
        self._strip.refresh(engine)
        for seg in self._segments:
            seg.refresh()
