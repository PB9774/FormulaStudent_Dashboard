"""
ui/pages/timer_page.py  [TABBED — one mode at a time]
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Timer & Stopwatch Page (Screen 4)

Driver picks ONE mode via tab buttons at the top:
  [⏱ STOPWATCH]  [⏳ COUNTDOWN]

Only the selected panel is visible. The other is hidden but its
internal timer continues running if active (pause-on-hide behaviour
can be toggled — currently pauses on tab switch).
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea, QSizePolicy,
    QStackedWidget,
)

from ui.styles.theme            import Color, Font
from ui.widgets.telemetry_strip import TelemetryStrip


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(ms: int) -> str:
    """Milliseconds → HH : MM : SS . cc"""
    ms  = max(0, ms)
    cs  = ms  // 10
    sec = cs  // 100;  cs  %= 100
    mn  = sec // 60;   sec %= 60
    hr  = mn  // 60;   mn  %= 60
    return f"{hr:02d} : {mn:02d} : {sec:02d} . {cs:02d}"


# ── Shared display style ──────────────────────────────────────────────────────

_DISPLAY_STYLE = (
    f"color:{Color.TIMER_DIGIT}; font-family:{Font.MONO}; "
    f"font-size:64px; font-weight:900; background:transparent; border:none;"
)

_DISPLAY_WARN = (
    f"color:{Color.RED}; font-family:{Font.MONO}; "
    f"font-size:64px; font-weight:900; background:transparent; border:none;"
)


# ══════════════════════════════════════════════════════════════════════════════
# STOPWATCH PANEL
# ══════════════════════════════════════════════════════════════════════════════

class _Stopwatch(QWidget):
    """Start / Pause / Lap / Reset — lap list with BEST/SLOW badges."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._elapsed_ms = 0
        self._running    = False
        self._laps: list[int] = []

        self._tick = QTimer(self)
        self._tick.setInterval(20)    # 50 Hz
        self._tick.timeout.connect(self._on_tick)

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        # ── Big display ──
        self._lbl = QLabel("00 : 00 : 00 . 00")
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl.setStyleSheet(_DISPLAY_STYLE)
        root.addWidget(self._lbl)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._btn_start = QPushButton("▶  START")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.setFixedHeight(52)
        self._btn_start.clicked.connect(self._toggle)

        self._btn_lap = QPushButton("⏺  LAP")
        self._btn_lap.setObjectName("btn_lap")
        self._btn_lap.setFixedHeight(52)
        self._btn_lap.setEnabled(False)
        self._btn_lap.clicked.connect(self._lap)

        self._btn_reset = QPushButton("↺  RESET")
        self._btn_reset.setObjectName("btn_reset")
        self._btn_reset.setFixedHeight(52)
        self._btn_reset.clicked.connect(self._reset)

        btn_row.addWidget(self._btn_start, 3)
        btn_row.addWidget(self._btn_lap,   2)
        btn_row.addWidget(self._btn_reset, 2)
        root.addLayout(btn_row)

        # ── Lap header ──
        lap_hdr = QLabel("LAP  TIMES")
        lap_hdr.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-size:{Font.SIZE_XS}px; "
            f"font-weight:700; letter-spacing:2px;"
        )
        root.addWidget(lap_hdr)

        # ── Lap scroll list ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:transparent; border:1px solid " + Color.BORDER + "; border-radius:10px;")

        self._lap_container = QWidget()
        self._lap_container.setStyleSheet("background:transparent;")
        self._lap_lay = QVBoxLayout(self._lap_container)
        self._lap_lay.setContentsMargins(6, 6, 6, 6)
        self._lap_lay.setSpacing(4)
        self._lap_lay.addStretch()
        scroll.setWidget(self._lap_container)
        root.addWidget(scroll, 1)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _toggle(self) -> None:
        if self._running:
            self._tick.stop()
            self._running = False
            self._btn_start.setText("▶  START")
            self._btn_start.setObjectName("btn_start")
            self._btn_start.setStyle(self._btn_start.style())
            self._btn_lap.setEnabled(False)
        else:
            self._tick.start()
            self._running = True
            self._btn_start.setText("⏸  PAUSE")
            self._btn_start.setObjectName("btn_stop")
            self._btn_start.setStyle(self._btn_start.style())
            self._btn_lap.setEnabled(True)

    def _on_tick(self) -> None:
        self._elapsed_ms += 20
        self._lbl.setText(_fmt(self._elapsed_ms))

    def _lap(self) -> None:
        self._laps.append(self._elapsed_ms)
        n = len(self._laps)

        is_best  = n > 1 and self._laps[-1] == min(self._laps)
        is_worst = n > 1 and self._laps[-1] == max(self._laps)
        color = Color.NEON_GREEN if is_best else (Color.RED if is_worst else Color.TEXT_PRI)

        row = QFrame()
        row.setStyleSheet(
            f"background:{Color.BG_CARD2}; border-radius:6px; border:1px solid {Color.BORDER};"
        )
        row_l = QHBoxLayout(row)
        row_l.setContentsMargins(10, 4, 10, 4)
        row_l.setSpacing(10)

        num_l = QLabel(f"#{n:02d}")
        num_l.setFixedWidth(30)
        num_l.setStyleSheet(
            f"color:{Color.ACCENT_BLUE}; font-family:{Font.MONO}; "
            f"font-size:{Font.SIZE_SM}px; font-weight:800; background:transparent; border:none;"
        )

        time_l = QLabel(_fmt(self._elapsed_ms))
        time_l.setStyleSheet(
            f"color:{color}; font-family:{Font.MONO}; "
            f"font-size:{Font.SIZE_SM}px; font-weight:700; background:transparent; border:none;"
        )

        badge_txt = "● BEST" if is_best else ("● SLOW" if is_worst else "")
        badge_l   = QLabel(badge_txt)
        badge_l.setStyleSheet(
            f"color:{color}; font-size:{Font.SIZE_XS}px; font-weight:700; "
            f"background:transparent; border:none;"
        )

        row_l.addWidget(num_l)
        row_l.addWidget(time_l)
        row_l.addStretch()
        row_l.addWidget(badge_l)

        # Insert before stretch
        self._lap_lay.insertWidget(self._lap_lay.count() - 1, row)

    def _reset(self) -> None:
        self._tick.stop()
        self._running    = False
        self._elapsed_ms = 0
        self._laps.clear()
        self._lbl.setText("00 : 00 : 00 . 00")
        self._lbl.setStyleSheet(_DISPLAY_STYLE)
        self._btn_start.setText("▶  START")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.setStyle(self._btn_start.style())
        self._btn_lap.setEnabled(False)
        while self._lap_lay.count() > 1:
            item = self._lap_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def pause_if_running(self) -> None:
        if self._running:
            self._toggle()


# ══════════════════════════════════════════════════════════════════════════════
# COUNTDOWN TIMER PANEL
# ══════════════════════════════════════════════════════════════════════════════

class _Countdown(QWidget):
    """Countdown with +/− preset buttons. Turns red and alerts at zero."""

    DEFAULT_MS = 5 * 60 * 1000

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._total_ms  = self.DEFAULT_MS
        self._remain    = self._total_ms
        self._running   = False

        self._tick = QTimer(self)
        self._tick.setInterval(20)
        self._tick.timeout.connect(self._on_tick)

        self._build_ui()
        self._update_display()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        # ── Big display ──
        self._lbl = QLabel("00 : 05 : 00 . 00")
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl.setStyleSheet(_DISPLAY_STYLE)
        root.addWidget(self._lbl)

        # ── Preset adjust row ──
        preset_row = QHBoxLayout()
        preset_row.setSpacing(8)

        set_lbl = QLabel("SET :")
        set_lbl.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_SM}px; font-weight:700;"
        )
        preset_row.addWidget(set_lbl)

        for label, delta_ms in [
            ("+1 m",   60_000),
            ("+5 m",  300_000),
            ("+10 m", 600_000),
            ("−1 m",  -60_000),
            ("−5 m", -300_000),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("btn_pill")
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda _, d=delta_ms: self._adjust(d))
            preset_row.addWidget(btn)

        preset_row.addStretch()
        root.addLayout(preset_row)

        # ── Status label ──
        self._lbl_status = QLabel("")
        self._lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_status.setFixedHeight(28)
        self._lbl_status.setStyleSheet(
            f"color:{Color.RED}; font-size:{Font.SIZE_LG}px; "
            f"font-weight:800; background:transparent; border:none;"
        )
        root.addWidget(self._lbl_status)

        # ── Control buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._btn_start = QPushButton("▶  START")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.setFixedHeight(52)
        self._btn_start.clicked.connect(self._toggle)

        self._btn_reset = QPushButton("↺  RESET")
        self._btn_reset.setObjectName("btn_reset")
        self._btn_reset.setFixedHeight(52)
        self._btn_reset.clicked.connect(self._reset)

        btn_row.addWidget(self._btn_start, 2)
        btn_row.addWidget(self._btn_reset, 1)
        root.addLayout(btn_row)

        root.addStretch()

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _update_display(self) -> None:
        self._lbl.setText(_fmt(self._remain))
        style = _DISPLAY_WARN if self._remain <= 10_000 else _DISPLAY_STYLE
        self._lbl.setStyleSheet(style)

    def _toggle(self) -> None:
        if self._remain <= 0:
            return
        if self._running:
            self._tick.stop()
            self._running = False
            self._btn_start.setText("▶  START")
            self._btn_start.setObjectName("btn_start")
            self._btn_start.setStyle(self._btn_start.style())
        else:
            self._tick.start()
            self._running = True
            self._btn_start.setText("⏸  PAUSE")
            self._btn_start.setObjectName("btn_stop")
            self._btn_start.setStyle(self._btn_start.style())
            self._lbl_status.setText("")

    def _on_tick(self) -> None:
        self._remain = max(0, self._remain - 20)
        self._update_display()
        if self._remain == 0:
            self._tick.stop()
            self._running = False
            self._btn_start.setText("▶  START")
            self._btn_start.setObjectName("btn_start")
            self._btn_start.setStyle(self._btn_start.style())
            self._lbl_status.setText("⏰  TIME'S UP !")

    def _adjust(self, delta_ms: int) -> None:
        if self._running:
            return
        self._total_ms = max(0, self._total_ms + delta_ms)
        self._remain   = self._total_ms
        self._lbl_status.setText("")
        self._update_display()

    def _reset(self) -> None:
        self._tick.stop()
        self._running = False
        self._remain  = self._total_ms
        self._btn_start.setText("▶  START")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.setStyle(self._btn_start.style())
        self._lbl_status.setText("")
        self._update_display()

    def pause_if_running(self) -> None:
        if self._running:
            self._toggle()


# ══════════════════════════════════════════════════════════════════════════════
# TIMER PAGE  (tabbed — one mode at a time)
# ══════════════════════════════════════════════════════════════════════════════

class TimerPage(QWidget):
    """
    Screen 4 — Timer & Stopwatch.
    Two tab buttons at top switch between modes.
    Only one panel visible at a time.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._strip = TelemetryStrip()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(12)

        # Telemetry strip
        root.addWidget(self._strip)

        # ── Page title ──
        title_row = QHBoxLayout()
        title = QLabel("TIMER  &  STOPWATCH")
        title.setObjectName("page_header")
        title_row.addWidget(title)
        title_row.addStretch()
        root.addLayout(title_row)

        # ── Tab selector ──
        tab_frame = QFrame()
        tab_frame.setObjectName("card")
        tab_frame.setFixedHeight(52)
        tab_lay = QHBoxLayout(tab_frame)
        tab_lay.setContentsMargins(10, 8, 10, 8)
        tab_lay.setSpacing(10)

        self._btn_sw  = QPushButton("⏱   STOPWATCH")
        self._btn_cd  = QPushButton("⏳   COUNTDOWN")

        for btn in (self._btn_sw, self._btn_cd):
            btn.setObjectName("btn_pill")
            btn.setCheckable(True)
            btn.setFixedHeight(36)

        self._btn_sw.setChecked(True)
        self._btn_sw.clicked.connect(lambda: self._switch(0))
        self._btn_cd.clicked.connect(lambda: self._switch(1))

        tab_lay.addWidget(self._btn_sw)
        tab_lay.addWidget(self._btn_cd)
        tab_lay.addStretch()
        root.addWidget(tab_frame)

        # ── Stacked panels ──
        self._stack = QStackedWidget()

        # Content wrapper gives padding inside the card
        self._sw_panel = self._wrap_panel(_Stopwatch())
        self._cd_panel = self._wrap_panel(_Countdown())

        self._stopwatch = self._sw_panel.findChild(_Stopwatch)
        self._countdown = self._cd_panel.findChild(_Countdown)

        self._stack.addWidget(self._sw_panel)   # 0
        self._stack.addWidget(self._cd_panel)   # 1
        root.addWidget(self._stack, 1)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _wrap_panel(self, widget: QWidget) -> QFrame:
        """Wrap a panel in a card frame with padding."""
        frame = QFrame()
        frame.setObjectName("card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(0)
        lay.addWidget(widget)
        return frame

    def _switch(self, idx: int) -> None:
        # Pause whichever is currently running
        if self._stopwatch:
            self._stopwatch.pause_if_running()
        if self._countdown:
            self._countdown.pause_if_running()

        self._stack.setCurrentIndex(idx)
        self._btn_sw.setChecked(idx == 0)
        self._btn_cd.setChecked(idx == 1)

    # ── Page lifecycle ────────────────────────────────────────────────────────

    def refresh(self, engine=None) -> None:
        if engine is not None:
            self._strip.refresh(engine)
