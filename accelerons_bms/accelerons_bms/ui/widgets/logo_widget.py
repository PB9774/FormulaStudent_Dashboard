"""
ui/widgets/logo_widget.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Brand Logo Widget
QPainter-rendered logo: lightning bolt ⚡ + styled text.
Scales cleanly at any size.
"""

from PyQt6.QtCore  import Qt, QRectF, QPointF
from PyQt6.QtGui   import (
    QPainter, QPen, QColor, QFont, QPolygonF,
    QLinearGradient, QPainterPath,
)
from PyQt6.QtWidgets import QWidget


class LogoWidget(QWidget):
    """
    Draws the Accelerons Electric brand logo inline.

    Layout:  [⚡ bolt]  ACCELERONS  ELECTRIC
    The bolt is a filled polygon with a blue→orange gradient.
    """

    def __init__(self, height: int = 36, parent=None) -> None:
        super().__init__(parent)
        self._h = height
        self.setFixedHeight(height)
        self.setSizePolicy(
            __import__("PyQt6.QtWidgets", fromlist=["QSizePolicy"]).QSizePolicy.Policy.Fixed,
            __import__("PyQt6.QtWidgets", fromlist=["QSizePolicy"]).QSizePolicy.Policy.Fixed,
        )
        # Estimate width: bolt + gap + text
        self.setFixedWidth(int(height * 9.5))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, _event) -> None:           # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        h   = float(self.height())
        bw  = h * 0.55     # bolt width
        gap = h * 0.18

        # ── Lightning bolt polygon ────────────────────────────────────────────
        # Classic bolt shape: top-right, middle-right, bottom-left, middle-left
        cx = bw / 2
        pts = [
            QPointF(cx + bw * 0.12,  h * 0.02),   # top-right
            QPointF(cx - bw * 0.06,  h * 0.48),   # mid-left
            QPointF(cx + bw * 0.18,  h * 0.44),   # mid-right notch
            QPointF(cx - bw * 0.12,  h * 0.98),   # bottom-left
            QPointF(cx + bw * 0.06,  h * 0.52),   # mid-right
            QPointF(cx - bw * 0.18,  h * 0.56),   # mid-left notch
        ]
        bolt = QPolygonF(pts)

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#1D4ED8"))   # blue top
        grad.setColorAt(1.0, QColor("#EA580C"))   # orange bottom

        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(bolt)

        # ── "ACCELERONS" text ─────────────────────────────────────────────────
        x_text = bw + gap
        font1 = QFont("Roboto", int(h * 0.42), QFont.Weight.Black)
        font1.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, h * 0.06)
        p.setFont(font1)
        p.setPen(QColor("#1D4ED8"))
        p.drawText(
            QRectF(x_text, 0, h * 5.4, h * 0.58),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "ACCELERONS",
        )

        # ── "ELECTRIC" text ───────────────────────────────────────────────────
        font2 = QFont("Roboto", int(h * 0.34), QFont.Weight.Bold)
        font2.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, h * 0.10)
        p.setFont(font2)
        p.setPen(QColor("#EA580C"))
        p.drawText(
            QRectF(x_text + h * 0.05, h * 0.52, h * 5.4, h * 0.52),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "ELECTRIC",
        )

        p.end()
