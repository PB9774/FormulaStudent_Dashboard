"""
ui/widgets/nav_bar.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Bottom Navigation Bar (5 tabs)
"""

from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtGui     import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton


_NAV_ITEMS = [
    ("⬡",  "Dashboard"),
    ("▦",  "Heatmap"),
    ("∿",  "Analytics"),
    ("⏱",  "Timer"),
    ("🗂",  "Storage"),
]


class NavBar(QWidget):
    """Horizontal tab bar — 5 tabs."""

    page_changed = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("nav_bar")
        self.setFixedHeight(58)
        self._buttons: list[QPushButton] = []
        self._build_ui()
        self._select(0)

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 4, 0, 4)
        root.setSpacing(0)
        for idx, (icon, label) in enumerate(_NAV_ITEMS):
            btn = self._make_tab(idx, icon, label)
            self._buttons.append(btn)
            root.addWidget(btn)

    def _make_tab(self, idx: int, icon: str, label: str) -> QPushButton:
        btn = QPushButton(f"{icon}\n{label}")
        btn.setObjectName("nav_btn")
        btn.setCheckable(True)
        btn.setFlat(True)
        btn.setFont(QFont("Roboto", 9))
        btn.clicked.connect(lambda _, i=idx: self._select(i))
        return btn

    def _select(self, idx: int) -> None:
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == idx)
        self.page_changed.emit(idx)

    def set_page(self, idx: int) -> None:
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == idx)
