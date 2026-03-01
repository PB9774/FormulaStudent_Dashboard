"""
ui/pages/analytics_page.py  [GRAPH FIXES]
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Analytics Page (Screen 3)

Graph fixes:
  • Time stored as positive elapsed seconds (0 → ∞)
  • Window = [latest_t - window_s  →  latest_t]  — slides forward indefinitely
  • Data always flows LEFT → RIGHT like an oscilloscope
  • No freeze — window always anchors to the newest sample
"""

import numpy as np
import pyqtgraph as pg

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QButtonGroup, QSizePolicy,
)

from ui.styles.theme            import Color, Font
from ui.widgets.telemetry_strip import TelemetryStrip
from core.data_engine           import DataEngine

pg.setConfigOptions(antialias=True, background=Color.BG_CARD, foreground=Color.TEXT_SEC)


# ── Chart configs ─────────────────────────────────────────────────────────────

_CHARTS = [
    dict(title="CURRENT",   unit="A",  color="#1D4ED8", min_y=-10,  max_y=120),
    dict(title="SOC",       unit="%",  color="#16A34A", min_y=0,    max_y=100),
    dict(title="AVG  TEMP", unit="°C", color="#B45309", min_y=15,   max_y=55),
]

_RANGES = [
    ("1 m",   60),
    ("5 m",  300),
    ("10 m", 600),
    ("20 m", 1200),
    ("30 m", 1800),
]

_DEFAULT_RANGE = 300   # 5 minutes


# ── Styled plot widget ────────────────────────────────────────────────────────

class _StyledPlot(pg.PlotWidget):
    """
    One live-updating line graph.

    X axis = absolute elapsed seconds (positive, always increasing).
    The visible window = [t_latest - window_s  →  t_latest].
    As time passes the window slides right — data flows left → right.
    """

    def __init__(self, title: str, unit: str, color: str,
                 min_y: float, max_y: float) -> None:
        super().__init__()

        self.setBackground(Color.BG_CARD)
        self.showGrid(x=True, y=True, alpha=0.15)
        self.setMenuEnabled(False)
        self.setMouseEnabled(x=False, y=False)

        # Y axis — fixed range
        self.setYRange(min_y, max_y, padding=0.05)

        axis_style = {"color": Color.TEXT_SEC, "font-size": "9pt"}
        self.getAxis("left").setLabel(f"{title} ({unit})", **axis_style)
        self.getAxis("left").setTextPen(pg.mkPen(color=Color.SLATE))
        self.getAxis("left").setPen(pg.mkPen(color=Color.BORDER))
        self.getAxis("bottom").setTextPen(pg.mkPen(color=Color.SLATE))
        self.getAxis("bottom").setPen(pg.mkPen(color=Color.BORDER))
        self.getAxis("bottom").setLabel("elapsed (s)", **axis_style)

        self.setTitle(
            f"<span style='color:{color}; font-size:10pt; font-weight:700;"
            f" letter-spacing:2px;'>{title}</span>"
        )

        # Filled area under line
        self._line = self.plot([], [], pen=pg.mkPen(color=color, width=2), antialias=True)

        import pyqtgraph as _pg
        from PyQt6.QtGui import QColor
        fill_color = QColor(color)
        fill_color.setAlpha(25)
        self._baseline = self.plot([], [], pen=pg.mkPen(color=color, width=0))
        self._fill = _pg.FillBetweenItem(self._line, self._baseline,
                                          brush=_pg.mkBrush(fill_color))
        self.addItem(self._fill)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update_data(self, times: list, values: list, window_s: float) -> None:
        """
        times  : list of positive elapsed seconds, oldest first
        values : matching list of measurements
        window_s: how many seconds of history to show
        """
        if len(times) < 2:
            return

        t = np.array(times,  dtype=np.float64)
        v = np.array(values, dtype=np.float64)

        # Latest sample defines the right edge of the window
        t_max = t[-1]
        t_min = t_max - window_s

        # Mask to the visible window only
        mask = t >= t_min
        t_vis = t[mask]
        v_vis = v[mask]

        if len(t_vis) < 2:
            return

        self._line.setData(t_vis, v_vis)
        self._baseline.setData([t_vis[0], t_vis[-1]], [v_vis.min(), v_vis.min()])

        # X axis always anchors to newest data, slides forward
        self.setXRange(t_min, t_max, padding=0)


# ── Analytics page ────────────────────────────────────────────────────────────

class AnalyticsPage(QWidget):
    """
    Screen 3 — Analytics.
    Three stacked live graphs with selectable time-range pills.
    """

    def __init__(self, engine: DataEngine, parent=None) -> None:
        super().__init__(parent)
        self._engine       = engine
        self._window_s     = _DEFAULT_RANGE
        self._plots: list[_StyledPlot] = []
        self._btn_group    = QButtonGroup(self)
        self._strip        = TelemetryStrip()
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(8)

        root.addWidget(self._strip)
        root.addWidget(self._build_header())

        for cfg in _CHARTS:
            plot = _StyledPlot(**cfg)
            self._plots.append(plot)
            root.addWidget(plot, 1)

        root.addWidget(self._build_range_bar())

    def _build_header(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)

        title = QLabel("ANALYTICS")
        title.setObjectName("page_header")

        self._lbl_rate = QLabel("● 10 Hz  |  live")
        self._lbl_rate.setStyleSheet(
            f"color:{Color.NEON_GREEN}; font-size:{Font.SIZE_SM}px; font-weight:700;"
        )

        lay.addWidget(title)
        lay.addStretch()
        lay.addWidget(self._lbl_rate)
        return w

    def _build_range_bar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setFixedHeight(46)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(14, 6, 14, 6)
        lay.setSpacing(8)

        lbl = QLabel("WINDOW")
        lbl.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_XS}px; "
            f"letter-spacing:2px; font-weight:700;"
        )
        lay.addWidget(lbl)
        lay.addSpacing(4)

        for label, seconds in _RANGES:
            btn = QPushButton(label)
            btn.setObjectName("btn_pill")
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setChecked(seconds == _DEFAULT_RANGE)
            btn.clicked.connect(lambda _, s=seconds: self._set_window(s))
            self._btn_group.addButton(btn)
            lay.addWidget(btn)

        lay.addStretch()

        # Elapsed counter
        self._lbl_elapsed = QLabel("t = 0 s")
        self._lbl_elapsed.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-family:{Font.MONO}; font-size:{Font.SIZE_XS}px;"
        )
        lay.addWidget(self._lbl_elapsed)
        return frame

    # ── Range selection ───────────────────────────────────────────────────────

    def _set_window(self, seconds: int) -> None:
        self._window_s = seconds

    # ── Refresh (10 Hz) ───────────────────────────────────────────────────────

    def refresh(self, engine: DataEngine) -> None:
        self._strip.refresh(engine)
        times    = list(engine.time_history)
        currents = list(engine.current_history)
        socs     = list(engine.soc_history)
        temps    = list(engine.temp_history)

        if times:
            self._lbl_elapsed.setText(f"t = {times[-1]:.0f} s")

        for plot, values in zip(self._plots, [currents, socs, temps]):
            plot.update_data(times, values, self._window_s)
