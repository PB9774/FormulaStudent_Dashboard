"""
ui/widgets/telemetry_strip.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Persistent Telemetry Strip
A compact bar shown at the top of pages 2, 3, 4 giving the driver
always-visible SOC and Speed readings.

Layout:
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚡ ACCELERONS  │  ▶  44.9 km/h  │  SOC  86.2%  ██████████░░  │  14:32 │
└─────────────────────────────────────────────────────────────────────────┘
"""

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QFrame, QProgressBar, QSizePolicy,
)
from ui.styles.theme        import Color, Font
from ui.widgets.logo_widget import LogoWidget


class TelemetryStrip(QFrame):
    """
    Compact persistent strip — attaches to top of any page.
    Call refresh(engine) at 10 Hz to update.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedHeight(44)
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 14, 0)
        lay.setSpacing(0)

        # ── Small logo ──────────────────────────────────────────────────────
        logo = LogoWidget(height=26)
        lay.addWidget(logo)

        # ── Divider ──────────────────────────────────────────────────────────
        lay.addWidget(self._vdiv())

        # ── Speed block ──────────────────────────────────────────────────────
        spd_w = QWidget()
        spd_l = QHBoxLayout(spd_w)
        spd_l.setContentsMargins(14, 0, 14, 0)
        spd_l.setSpacing(6)

        spd_tag = QLabel("SPEED")
        spd_tag.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-size:{Font.SIZE_XS}px; "
            f"font-weight:700; letter-spacing:2px; background:transparent; border:none;"
        )

        self._lbl_speed = QLabel("--.- km/h")
        self._lbl_speed.setStyleSheet(
            f"color:{Color.AMBER}; font-family:{Font.MONO}; "
            f"font-size:22px; font-weight:900; background:transparent; border:none;"
        )

        spd_l.addWidget(spd_tag, alignment=Qt.AlignmentFlag.AlignVCenter)
        spd_l.addWidget(self._lbl_speed, alignment=Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(spd_w)

        # ── Divider ──────────────────────────────────────────────────────────
        lay.addWidget(self._vdiv())

        # ── SOC block ────────────────────────────────────────────────────────
        soc_w = QWidget()
        soc_l = QHBoxLayout(soc_w)
        soc_l.setContentsMargins(14, 4, 14, 4)
        soc_l.setSpacing(8)
        soc_w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        soc_tag = QLabel("SOC")
        soc_tag.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-size:{Font.SIZE_XS}px; "
            f"font-weight:700; letter-spacing:2px; background:transparent; border:none;"
        )

        self._lbl_soc = QLabel("--.- %")
        self._lbl_soc.setFixedWidth(68)
        self._lbl_soc.setStyleSheet(
            f"color:{Color.NEON_GREEN}; font-family:{Font.MONO}; "
            f"font-size:18px; font-weight:900; background:transparent; border:none;"
        )

        self._soc_bar = QProgressBar()
        self._soc_bar.setRange(0, 1000)
        self._soc_bar.setTextVisible(False)
        self._soc_bar.setFixedHeight(10)
        self._soc_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._soc_bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:4px;}}"
            f"QProgressBar::chunk{{background:{Color.NEON_GREEN};border-radius:4px;}}"
        )

        soc_l.addWidget(soc_tag, alignment=Qt.AlignmentFlag.AlignVCenter)
        soc_l.addWidget(self._lbl_soc, alignment=Qt.AlignmentFlag.AlignVCenter)
        soc_l.addWidget(self._soc_bar, alignment=Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(soc_w)

    def _vdiv(self) -> QFrame:
        d = QFrame()
        d.setFixedSize(1, 28)
        d.setStyleSheet(f"background:{Color.BORDER};")
        return d

    def refresh(self, engine) -> None:
        speed = engine.speed
        soc   = engine.soc

        self._lbl_speed.setText(f"{speed:.1f} km/h")

        soc_color = (
            Color.NEON_GREEN if soc > 40 else
            Color.AMBER      if soc > 20 else
            Color.RED
        )
        self._lbl_soc.setText(f"{soc:.1f} %")
        self._lbl_soc.setStyleSheet(
            f"color:{soc_color}; font-family:{Font.MONO}; "
            f"font-size:18px; font-weight:900; background:transparent; border:none;"
        )
        self._soc_bar.setValue(int(soc * 10))
        self._soc_bar.setStyleSheet(
            f"QProgressBar{{background:{Color.BG_PANEL};border:none;border-radius:4px;}}"
            f"QProgressBar::chunk{{background:{soc_color};border-radius:4px;}}"
        )
