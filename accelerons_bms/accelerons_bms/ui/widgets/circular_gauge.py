"""
ui/widgets/circular_gauge.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Circular Gauge Widget
Custom QPainter widget rendering a glass-effect arc gauge.
"""

import math
from PyQt6.QtCore    import Qt, QRectF, QPointF
from PyQt6.QtGui     import (
    QPainter, QPen, QColor, QConicalGradient,
    QRadialGradient, QFont, QFontMetrics, QPainterPath
)
from PyQt6.QtWidgets import QWidget


class CircularGauge(QWidget):
    """
    Renders a glass-effect circular arc gauge.

    Parameters
    ----------
    label       : inner label (e.g. "SOC")
    unit        : unit string shown below value (e.g. "%")
    min_val     : minimum value
    max_val     : maximum value
    start_angle : arc start in degrees (0 = 3 o'clock, CCW)
    span_angle  : arc span in degrees
    color_normal: hex colour when value is in safe range
    warn_pct    : fraction of range at which amber warning starts
    crit_pct    : fraction of range at which red critical starts
    """

    def __init__(
        self,
        label:        str   = "SOC",
        unit:         str   = "%",
        min_val:      float = 0.0,
        max_val:      float = 100.0,
        start_angle:  int   = 225,
        span_angle:   int   = 270,
        color_normal: str   = "#39FF14",
        warn_pct:     float = 0.25,
        crit_pct:     float = 0.10,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._label        = label
        self._unit         = unit
        self._min          = min_val
        self._max          = max_val
        self._value        = min_val
        self._start_angle  = start_angle
        self._span_angle   = span_angle
        self._color_normal = QColor(color_normal)
        self._warn_pct     = warn_pct
        self._crit_pct     = crit_pct
        self.setMinimumSize(220, 220)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_value(self, value: float) -> None:
        self._value = max(self._min, min(self._max, value))
        self.update()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _fraction(self) -> float:
        rng = self._max - self._min
        return (self._value - self._min) / rng if rng else 0.0

    def _arc_color(self) -> QColor:
        frac = self._fraction()
        if frac <= self._crit_pct:
            return QColor("#FF3535")
        if frac <= self._warn_pct:
            return QColor("#FFB300")
        return self._color_normal

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _event) -> None:   # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side   = min(self.width(), self.height())
        margin = side * 0.08
        rect   = QRectF(
            (self.width()  - side) / 2 + margin,
            (self.height() - side) / 2 + margin,
            side - 2 * margin,
            side - 2 * margin,
        )
        cx, cy = rect.center().x(), rect.center().y()
        radius = rect.width() / 2

        # ── Track (background arc) ──
        track_pen = QPen(QColor("#E2E8F0"), int(side * 0.075), Qt.PenStyle.SolidLine)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, self._start_angle * 16, -self._span_angle * 16)

        # ── Value arc ──
        frac      = self._fraction()
        arc_color = self._arc_color()
        arc_span  = int(frac * self._span_angle)

        if arc_span > 0:
            val_pen = QPen(arc_color, int(side * 0.075), Qt.PenStyle.SolidLine)
            val_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(val_pen)
            painter.drawArc(rect, self._start_angle * 16, -arc_span * 16)

        # ── Glow ring (inner thin ring) ──
        glow_color = QColor(arc_color)
        glow_color.setAlpha(60)
        glow_pen = QPen(glow_color, int(side * 0.018), Qt.PenStyle.SolidLine)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        inner_offset = side * 0.052
        inner_rect = rect.adjusted(inner_offset, inner_offset, -inner_offset, -inner_offset)
        painter.setPen(glow_pen)
        if arc_span > 0:
            painter.drawArc(inner_rect, self._start_angle * 16, -arc_span * 16)

        # ── Glass inner circle (light theme: white with soft shadow) ──
        inner_r = radius * 0.70
        radial  = QRadialGradient(QPointF(cx, cy - inner_r * 0.2), inner_r)
        radial.setColorAt(0.0, QColor(255, 255, 255, 255))
        radial.setColorAt(0.75, QColor(240, 245, 252, 255))
        radial.setColorAt(1.0, QColor(220, 230, 242, 255))
        painter.setBrush(radial)
        painter.setPen(QPen(QColor("#CBD5E1"), 1))
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        # ── Glass sheen (top-left highlight) ──
        sheen_path = QPainterPath()
        sheen_path.addEllipse(QPointF(cx, cy), inner_r, inner_r)
        sheen_grad = QRadialGradient(QPointF(cx - inner_r * 0.3, cy - inner_r * 0.5), inner_r * 0.55)
        sheen_grad.setColorAt(0.0, QColor(255, 255, 255, 120))
        sheen_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(sheen_grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(sheen_path)

        # ── Value text ──
        val_text = f"{self._value:.1f}"
        font_val = QFont("Roboto Mono", int(side * 0.16), QFont.Weight.Bold)
        painter.setFont(font_val)
        painter.setPen(QPen(arc_color))
        painter.drawText(
            QRectF(cx - inner_r, cy - inner_r * 0.35, inner_r * 2, inner_r * 0.85),
            Qt.AlignmentFlag.AlignCenter,
            val_text,
        )

        # ── Unit text ──
        font_unit = QFont("Roboto", int(side * 0.07))
        painter.setFont(font_unit)
        painter.setPen(QPen(QColor("#64748B")))
        painter.drawText(
            QRectF(cx - inner_r, cy + inner_r * 0.10, inner_r * 2, inner_r * 0.40),
            Qt.AlignmentFlag.AlignCenter,
            self._unit,
        )

        # ── Label text ──
        font_lbl = QFont("Roboto", int(side * 0.065), QFont.Weight.Bold)
        font_lbl.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font_lbl)
        painter.setPen(QPen(QColor("#94A3B8")))
        painter.drawText(
            QRectF(cx - inner_r, cy - inner_r * 0.80, inner_r * 2, inner_r * 0.45),
            Qt.AlignmentFlag.AlignCenter,
            self._label,
        )

        painter.end()
