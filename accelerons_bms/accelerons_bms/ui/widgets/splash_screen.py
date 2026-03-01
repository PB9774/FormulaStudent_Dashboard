"""
ui/widgets/splash_screen.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Animated Splash Screen

Behaviour:
  1. Full-screen frameless window appears showing logo (file or painted).
  2. Hold for 1.8 s.
  3. Logo animates — shrinks and slides to top-left (its final header position).
  4. Emits `done` signal → main window shows, splash hides.

Logo loading priority:
  1. assets/logo.png  (user-placed)
  2. assets/logo.jpg
  3. assets/logo.svg  (via QSvgRenderer if available)
  4. Fallback → LogoWidget (painted in-code)
"""

from __future__ import annotations
import os

from PyQt6.QtCore    import (
    Qt, QTimer, QPropertyAnimation, QRect,
    QEasingCurve, pyqtSignal, QObject, QSize,
)
from PyQt6.QtGui     import (
    QPainter, QColor, QFont, QPixmap,
    QPen, QLinearGradient, QPolygonF,
)
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore    import QPointF

from ui.styles.theme import Color, Font


# ── Painted logo (fallback when no image file found) ─────────────────────────

def _paint_logo_pixmap(width: int, height: int) -> QPixmap:
    """Return a QPixmap with the Accelerons logo painted at given size."""
    pm = QPixmap(width, height)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    h   = float(height)
    bw  = h * 0.45
    gap = h * 0.16

    # Lightning bolt
    cx = bw / 2
    pts = [
        QPointF(cx + bw * 0.12,  h * 0.02),
        QPointF(cx - bw * 0.06,  h * 0.48),
        QPointF(cx + bw * 0.18,  h * 0.44),
        QPointF(cx - bw * 0.12,  h * 0.98),
        QPointF(cx + bw * 0.06,  h * 0.52),
        QPointF(cx - bw * 0.18,  h * 0.56),
    ]
    from PyQt6.QtGui import QPolygonF as _PF
    bolt = _PF(pts)
    grad = QLinearGradient(0, 0, 0, h)
    grad.setColorAt(0.0, QColor("#1D4ED8"))
    grad.setColorAt(1.0, QColor("#EA580C"))
    p.setBrush(grad)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawPolygon(bolt)

    x_text = bw + gap
    font1 = QFont("Roboto", int(h * 0.38), QFont.Weight.Black)
    font1.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, h * 0.06)
    p.setFont(font1)
    p.setPen(QColor("#1D4ED8"))
    from PyQt6.QtCore import QRectF
    p.drawText(QRectF(x_text, 0, width, h * 0.56),
               Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
               "ACCELERONS")

    font2 = QFont("Roboto", int(h * 0.30), QFont.Weight.Bold)
    font2.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, h * 0.10)
    p.setFont(font2)
    p.setPen(QColor("#EA580C"))
    p.drawText(QRectF(x_text + h * 0.05, h * 0.52, width, h * 0.52),
               Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
               "ELECTRIC")
    p.end()
    return pm


def _load_logo_pixmap(assets_dir: str, width: int, height: int) -> QPixmap | None:
    """Try to load logo from assets directory. Returns None if not found."""
    for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo.bmp"):
        path = os.path.join(assets_dir, name)
        if os.path.isfile(path):
            pm = QPixmap(path)
            if not pm.isNull():
                return pm.scaled(
                    width, height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
    return None


# ── Splash screen widget ──────────────────────────────────────────────────────

class SplashScreen(QWidget):
    """
    Full-screen animated splash.
    done signal fires when animation completes and main window should show.
    """

    done = pyqtSignal()

    # Final resting position of the logo in the main window header
    # (approximate — matches where LogoWidget sits in DashboardPage header)
    _FINAL_X     = 26          # px from left of main window
    _FINAL_Y     = 9           # px from top of main window
    _FINAL_H     = 30          # final logo height in header

    _HOLD_MS     = 1800        # hold splash before animating
    _ANIM_MS     = 700         # animation duration

    def __init__(self, assets_dir: str, parent=None) -> None:
        super().__init__(parent)
        self._assets_dir = assets_dir

        # Frameless full-screen
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(f"background: {Color.BG_BASE};")

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self._build_ui(screen.width(), screen.height())

        # Hold timer → triggers animation
        QTimer.singleShot(self._HOLD_MS, self._start_animation)

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_ui(self, sw: int, sh: int) -> None:
        # Logo — large, centered
        logo_h = min(sh // 5, 160)
        logo_w = int(logo_h * 9.0)

        # Try file logo first
        pm = _load_logo_pixmap(self._assets_dir, logo_w * 3, logo_h * 3)
        if pm is not None:
            pm = pm.scaled(logo_w, logo_h,
                           Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
        else:
            pm = _paint_logo_pixmap(logo_w, logo_h)

        self._logo_lbl = QLabel(self)
        self._logo_lbl.setPixmap(pm)
        self._logo_lbl.setFixedSize(logo_w, logo_h)
        self._logo_lbl.setScaledContents(True)

        # Centre logo
        lx = (sw - logo_w) // 2
        ly = (sh - logo_h) // 2 - sh // 10
        self._logo_lbl.move(lx, ly)

        # Tagline below logo
        self._tag = QLabel("Battery Management System", self)
        self._tag.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_LG}px; "
            f"font-weight:400; letter-spacing:4px; background:transparent;"
        )
        self._tag.adjustSize()
        self._tag.move(
            (sw - self._tag.width()) // 2,
            ly + logo_h + 18,
        )

        # Version / team
        self._ver = QLabel("v1.0  ·  Accelerons Electric Racing", self)
        self._ver.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-size:{Font.SIZE_SM}px; "
            f"background:transparent;"
        )
        self._ver.adjustSize()
        self._ver.move(
            (sw - self._ver.width()) // 2,
            ly + logo_h + 50,
        )

        # Loading dots
        self._dots = QLabel("● ● ●", self)
        self._dots.setStyleSheet(
            f"color:{Color.ACCENT_BLUE}; font-size:{Font.SIZE_SM}px; "
            f"letter-spacing:6px; background:transparent;"
        )
        self._dots.adjustSize()
        self._dots.move((sw - self._dots.width()) // 2, sh - 60)

        # Animate dots blinking
        self._dot_timer = QTimer(self)
        self._dot_timer.setInterval(400)
        self._dot_timer.timeout.connect(self._blink_dots)
        self._dot_timer.start()
        self._dot_state = 0

        # Store start geometry for animation
        self._start_rect = QRect(lx, ly, logo_w, logo_h)

    def _blink_dots(self) -> None:
        patterns = ["● ● ●", "○ ● ●", "● ○ ●", "● ● ○"]
        self._dot_state = (self._dot_state + 1) % len(patterns)
        self._dots.setText(patterns[self._dot_state])

    # ── Animation ─────────────────────────────────────────────────────────────

    def _start_animation(self) -> None:
        self._dot_timer.stop()
        self._dots.hide()
        self._tag.hide()
        self._ver.hide()

        # Fade background
        self.setStyleSheet(f"background: {Color.BG_BASE};")

        # Final small rect (where logo sits in main window header)
        final_h = self._FINAL_H
        final_w = int(final_h * 9.0)
        final_rect = QRect(self._FINAL_X, self._FINAL_Y, final_w, final_h)

        # Animate logo label geometry
        self._anim = QPropertyAnimation(self._logo_lbl, b"geometry")
        self._anim.setDuration(self._ANIM_MS)
        self._anim.setStartValue(self._start_rect)
        self._anim.setEndValue(final_rect)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.finished.connect(self._on_done)
        self._anim.start()

    def _on_done(self) -> None:
        self.done.emit()
        self.hide()
