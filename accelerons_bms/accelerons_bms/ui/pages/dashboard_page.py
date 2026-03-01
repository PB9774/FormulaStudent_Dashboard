"""
ui/pages/dashboard_page.py  [FITTED LAYOUT]
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Dashboard Page
• Elements properly sized — no dead space, no overflow
• Fault section enlarged — bigger text, more rows visible
• Clock reduced in header — not dominating
• Speed 110px, SOC 44px — readable on 5" TFT
"""

from __future__ import annotations
from typing import List
import datetime

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QPushButton, QSizePolicy,
)

from ui.styles.theme        import Color, Font
from ui.widgets.logo_widget import LogoWidget

_VOLT_MIN = 3.20
_VOLT_MAX  = 4.10


# ── Fault detection ───────────────────────────────────────────────────────────

def _detect_faults(engine) -> List[tuple]:
    faults = []
    dv = engine.delta_v
    if dv >= 0.06:
        faults.append(("F01", f"DV Critical  {dv:.3f}V", "crit"))
    elif dv >= 0.03:
        faults.append(("F01", f"DV Warning   {dv:.3f}V", "warn"))
    for m_idx, module in enumerate(engine.modules):
        for c_idx, cell in enumerate(module.cells):
            if cell.voltage > 3.90:
                faults.append((f"F{m_idx+2:02d}",
                    f"High  M{m_idx+1:02d}-C{c_idx+1:02d}  {cell.voltage:.3f}V", "crit"))
            elif cell.voltage < 3.40:
                faults.append((f"F{m_idx+2:02d}",
                    f"Low   M{m_idx+1:02d}-C{c_idx+1:02d}  {cell.voltage:.3f}V", "warn"))
    if engine.avg_temperature > 45:
        faults.append(("F10", f"High Temp  {engine.avg_temperature:.1f}C", "crit"))
    elif engine.avg_temperature > 38:
        faults.append(("F10", f"Temp Warn  {engine.avg_temperature:.1f}C", "warn"))
    return faults[:10]


# ── Segment summary row ───────────────────────────────────────────────────────

class _SegmentRow(QWidget):
    def __init__(self, idx: int, parent=None) -> None:
        super().__init__(parent)
        self._idx = idx
        self.setFixedHeight(26)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 1, 0, 1)
        lay.setSpacing(6)

        badge = QLabel(f"S{idx+1:02d}")
        badge.setFixedSize(24, 20)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"background:{Color.ACCENT_BLUE}; color:{Color.WHITE}; "
            f"border-radius:4px; font-size:{Font.SIZE_XS}px; font-weight:800;"
        )

        self._bar = QProgressBar()
        self._bar.setRange(0, 1000)
        self._bar.setTextVisible(False)
        self._bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._bar.setFixedHeight(8)
        self._bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{Color.GREEN_BAR};border-radius:3px;}}"
        )

        self._lbl_v = QLabel("-.---V")
        self._lbl_v.setFixedWidth(48)
        self._lbl_v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._lbl_v.setStyleSheet(
            f"color:{Color.NEON_GREEN}; font-family:{Font.MONO}; font-size:{Font.SIZE_XS}px; font-weight:700;"
        )

        self._lbl_t = QLabel("-.-C")
        self._lbl_t.setFixedWidth(38)
        self._lbl_t.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._lbl_t.setStyleSheet(
            f"color:{Color.AMBER}; font-family:{Font.MONO}; font-size:{Font.SIZE_XS}px; font-weight:700;"
        )

        lay.addWidget(badge)
        lay.addWidget(self._bar)
        lay.addWidget(self._lbl_v)
        lay.addWidget(self._lbl_t)

    def refresh(self, avg_v: float, avg_t: float) -> None:
        frac = max(0.0, min(1.0, (avg_v - _VOLT_MIN) / (_VOLT_MAX - _VOLT_MIN)))
        self._bar.setValue(int(frac * 1000))
        if avg_v < 3.40:   chunk, v_c = Color.AMBER_BAR, Color.AMBER
        elif avg_v > 3.90: chunk, v_c = Color.RED_BAR,   Color.RED
        else:              chunk, v_c = Color.GREEN_BAR,  Color.NEON_GREEN
        self._bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:3px;}}"
            f"QProgressBar::chunk{{background:{chunk};border-radius:3px;}}"
        )
        self._lbl_v.setText(f"{avg_v:.3f}V")
        self._lbl_v.setStyleSheet(
            f"color:{v_c}; font-family:{Font.MONO}; font-size:{Font.SIZE_XS}px; font-weight:700;"
        )
        self._lbl_t.setText(f"{avg_t:.1f}C")


# ── Fault card ────────────────────────────────────────────────────────────────

class _FaultCard(QFrame):
    """
    Live fault monitor — enlarged font and rows for readability.
    Shows up to 10 faults with clear severity colouring.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card_lit")
        self._build_ui()

    def _build_ui(self) -> None:
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(14, 12, 14, 12)
        self._root.setSpacing(8)

        # ── Header ──
        hdr = QHBoxLayout()

        title = QLabel("FAULT  MONITOR")
        title.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_SM}px; "
            f"font-weight:800; letter-spacing:2px;"
        )

        self._badge = QLabel("OK")
        self._badge.setFixedSize(42, 22)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setStyleSheet(
            f"background:{Color.NEON_GREEN}; color:{Color.WHITE}; "
            f"border-radius:5px; font-size:{Font.SIZE_SM}px; font-weight:800;"
        )

        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self._badge)
        self._root.addLayout(hdr)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{Color.BORDER};")
        self._root.addWidget(sep)

        # ── Fault rows container ──
        self._rows_w = QWidget()
        self._rows_l = QVBoxLayout(self._rows_w)
        self._rows_l.setContentsMargins(0, 0, 0, 0)
        self._rows_l.setSpacing(6)
        self._root.addWidget(self._rows_w)
        self._root.addStretch()

        self._show_ok()

    def _clear(self) -> None:
        while self._rows_l.count():
            item = self._rows_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_ok(self) -> None:
        self._clear()
        lbl = QLabel("●  All systems nominal")
        lbl.setStyleSheet(
            f"color:{Color.NEON_GREEN}; font-family:{Font.MONO}; "
            f"font-size:{Font.SIZE_MD}px; font-weight:700;"   # bigger than before
        )
        self._rows_l.addWidget(lbl)
        self._badge.setText("OK")
        self._badge.setStyleSheet(
            f"background:{Color.NEON_GREEN}; color:{Color.WHITE}; "
            f"border-radius:5px; font-size:{Font.SIZE_SM}px; font-weight:800;"
        )

    def update_faults(self, faults: list) -> None:
        if not faults:
            self._show_ok()
            return

        self._clear()
        crit = sum(1 for _, _, s in faults if s == "crit")
        badge_c = Color.RED if crit else Color.AMBER
        self._badge.setText(f"!{len(faults)}")
        self._badge.setStyleSheet(
            f"background:{badge_c}; color:{Color.WHITE}; "
            f"border-radius:5px; font-size:{Font.SIZE_SM}px; font-weight:800;"
        )

        for code, label, severity in faults:
            color  = Color.RED if severity == "crit" else Color.AMBER
            prefix = "▮" if severity == "crit" else "▲"

            row_w = QFrame()
            row_w.setStyleSheet(
                f"background:{Color.BG_CARD2}; border-radius:6px; border:1px solid {Color.BORDER};"
            )
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(8, 4, 8, 4)
            row_l.setSpacing(8)

            # Icon
            dot = QLabel(prefix)
            dot.setFixedWidth(14)
            dot.setStyleSheet(f"color:{color}; font-size:11px; background:transparent; border:none;")

            # Code badge
            code_lbl = QLabel(code)
            code_lbl.setFixedWidth(34)
            code_lbl.setStyleSheet(
                f"color:{color}; font-family:{Font.MONO}; "
                f"font-size:{Font.SIZE_SM}px; font-weight:800; background:transparent; border:none;"
            )

            # Message  — larger font than before
            msg_lbl = QLabel(label)
            msg_lbl.setStyleSheet(
                f"color:{Color.TEXT_PRI}; font-family:{Font.MONO}; "
                f"font-size:{Font.SIZE_SM}px; background:transparent; border:none;"
            )

            row_l.addWidget(dot)
            row_l.addWidget(code_lbl)
            row_l.addWidget(msg_lbl, 1)
            self._rows_l.addWidget(row_w)


# ── Dashboard page ────────────────────────────────────────────────────────────

class DashboardPage(QWidget):
    """
    Screen 1 — Dashboard.
    3-column: left (Pack V / Delta V / Segment Summary)
              centre (Speed / SOC)
              right (Fault Monitor / Save Logs)
    """

    def __init__(self, on_save_logs, parent=None) -> None:
        super().__init__(parent)
        self._on_save_logs  = on_save_logs
        self._segment_rows: list[_SegmentRow] = []
        self._build_ui()

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    # ── Root ──────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(8)

        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(10)
        body.addWidget(self._build_left_col(),   28)
        body.addWidget(self._build_centre_col(), 44)
        body.addWidget(self._build_right_col(),  28)
        root.addLayout(body, 1)

    # ── Header: Logo | small clock | Connected ────────────────────────────────

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card_lit")
        frame.setFixedHeight(56)          # taller to give logo breathing room
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(10)

        logo = LogoWidget(height=38)      # bigger logo
        lay.addWidget(logo)
        lay.addStretch()

        # Clock — compact
        self._lbl_clock = QLabel("--:--:--")
        self._lbl_clock.setStyleSheet(
            f"color:{Color.TEXT_PRI}; font-family:{Font.MONO}; "
            f"font-size:{Font.SIZE_LG}px; font-weight:700; "
            f"background:transparent; border:none;"
        )
        lay.addWidget(self._lbl_clock)
        lay.addStretch()

        self._lbl_connected = QLabel("●  Connected")
        self._lbl_connected.setStyleSheet(
            f"color:{Color.NEON_GREEN}; font-size:{Font.SIZE_SM}px; "
            f"font-weight:700; background:transparent; border:none;"
        )
        lay.addWidget(self._lbl_connected)
        return frame

    def _update_clock(self) -> None:
        self._lbl_clock.setText(datetime.datetime.now().strftime("%H:%M:%S"))

    # ── Left column ───────────────────────────────────────────────────────────

    def _build_left_col(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        lay.addWidget(self._build_stat_tile("PACK  VOLTAGE", "pack_v", Color.ACCENT_BLUE))
        lay.addWidget(self._build_stat_tile("DELTA  V  MAX−MIN", "dv", Color.AMBER))
        lay.addWidget(self._build_segment_summary(), 1)
        return w

    def _build_stat_tile(self, tag_text: str, attr: str, value_color: str) -> QFrame:
        """Generic key-value tile — fills full height with no dead space."""
        frame = QFrame()
        frame.setObjectName("card")
        frame.setFixedHeight(54)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(12, 0, 12, 0)

        tag = QLabel(tag_text)
        tag.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_XS}px; font-weight:700; "
            f"letter-spacing:1px; background:transparent; border:none;"
        )
        tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        val = QLabel("---")
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        val.setStyleSheet(
            f"color:{value_color}; font-family:{Font.MONO}; "
            f"font-size:{Font.SIZE_XL}px; font-weight:900; background:transparent; border:none;"
        )
        val.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        lay.addWidget(tag)
        lay.addWidget(val)

        # Store references for refresh
        setattr(self, f"_lbl_{attr}", val)
        return frame

    def _build_segment_summary(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(4)

        hdr = QLabel("SEGMENT  SUMMARY")
        hdr.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_XS}px; "
            f"font-weight:800; letter-spacing:2px;"
        )
        lay.addWidget(hdr)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{Color.BORDER};")
        lay.addWidget(sep)

        for i in range(7):
            row = _SegmentRow(i)
            self._segment_rows.append(row)
            lay.addWidget(row)

        lay.addStretch()
        return frame

    # ── Centre column ─────────────────────────────────────────────────────────

    def _build_centre_col(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        lay.addWidget(self._build_speed_card(), 5)
        lay.addWidget(self._build_soc_card(), 2)
        return w

    def _build_speed_card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card_lit")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(12, 8, 12, 6)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tag = QLabel("SPEED")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_SM}px; font-weight:800; "
            f"letter-spacing:6px; background:transparent; border:none;"
        )

        self._lbl_speed = QLabel("0.0")
        self._lbl_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_speed.setStyleSheet(
            f"color:{Color.AMBER}; font-family:{Font.MONO}; "
            f"font-size:110px; font-weight:900; background:transparent; border:none;"
        )
        self._lbl_speed.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        unit = QLabel("km / h")
        unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        unit.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-size:{Font.SIZE_MD}px; "
            f"letter-spacing:4px; background:transparent; border:none;"
        )

        lay.addWidget(tag)
        lay.addWidget(self._lbl_speed, 1)
        lay.addWidget(unit)
        return frame

    def _build_soc_card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(6)

        top = QHBoxLayout()
        lbl_tag = QLabel("SOC :")
        lbl_tag.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_SM}px; font-weight:800; "
            f"letter-spacing:2px; background:transparent; border:none;"
        )
        self._lbl_soc_val = QLabel("--.-  %")
        self._lbl_soc_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._lbl_soc_val.setStyleSheet(
            f"color:{Color.NEON_GREEN}; font-family:{Font.MONO}; "
            f"font-size:44px; font-weight:900; background:transparent; border:none;"
        )
        top.addWidget(lbl_tag, alignment=Qt.AlignmentFlag.AlignVCenter)
        top.addStretch()
        top.addWidget(self._lbl_soc_val)
        lay.addLayout(top)

        self._soc_bar = QProgressBar()
        self._soc_bar.setRange(0, 1000)
        self._soc_bar.setTextVisible(False)
        self._soc_bar.setFixedHeight(16)
        self._soc_bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:7px;}}"
            f"QProgressBar::chunk{{background:{Color.NEON_GREEN};border-radius:7px;}}"
        )
        lay.addWidget(self._soc_bar)
        return frame

    # ── Right column ──────────────────────────────────────────────────────────

    def _build_right_col(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._fault_card = _FaultCard()
        lay.addWidget(self._fault_card, 1)
        lay.addWidget(self._build_save_button())
        return w

    def _build_save_button(self) -> QPushButton:
        btn = QPushButton("  SAVE  LOGS")
        btn.setObjectName("btn_primary")
        btn.setFixedHeight(46)
        btn.clicked.connect(self._on_save_logs)
        return btn

    # ── 10 Hz refresh ─────────────────────────────────────────────────────────

    def refresh(self, engine) -> None:
        self._lbl_pack_v.setText(f"{engine.pack_voltage:.1f}V")

        dv = engine.delta_v
        dv_color = (Color.NEON_GREEN if dv < 0.03 else
                    Color.AMBER      if dv < 0.06 else Color.RED)
        self._lbl_dv.setText(f"{dv:.3f}V")
        self._lbl_dv.setStyleSheet(
            f"color:{dv_color}; font-family:{Font.MONO}; "
            f"font-size:{Font.SIZE_XL}px; font-weight:900; background:transparent; border:none;"
        )

        self._lbl_speed.setText(f"{engine.speed:.1f}")

        soc = engine.soc
        soc_color = (Color.NEON_GREEN if soc > 40 else
                     Color.AMBER      if soc > 20 else Color.RED)
        self._lbl_soc_val.setText(f"{soc:.1f}  %")
        self._lbl_soc_val.setStyleSheet(
            f"color:{soc_color}; font-family:{Font.MONO}; "
            f"font-size:44px; font-weight:900; background:transparent; border:none;"
        )
        self._soc_bar.setValue(int(soc * 10))
        self._soc_bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:7px;}}"
            f"QProgressBar::chunk{{background:{soc_color};border-radius:7px;}}"
        )

        for i, row in enumerate(self._segment_rows):
            row.refresh(engine.module_avg_voltage(i), engine.module_avg_temp(i))

        self._fault_card.update_faults(_detect_faults(engine))
