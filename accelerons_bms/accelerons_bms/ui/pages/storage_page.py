"""
ui/pages/storage_page.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Storage Page (Screen 4)
• Clean file explorer: CSV log files with timestamps and Download icons
• Refreshes list on every visit (via showEvent)
• Opens log folder in OS file manager on Download click
"""

import os
import subprocess
import sys

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QPushButton, QSizePolicy,
    QMessageBox,
)

from ui.styles.theme import Color, Font
from core.logger     import SessionLogger


class _FileRow(QFrame):
    """One CSV file row: icon | name | size | date | Download button."""

    def __init__(self, name: str, size: str, mtime: str, path: str, parent=None) -> None:
        super().__init__(parent)
        self._path = path
        self.setObjectName("card")
        self.setFixedHeight(56)
        self._build_ui(name, size, mtime)

    def _build_ui(self, name: str, size: str, mtime: str) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 8, 14, 8)
        root.setSpacing(12)

        # File icon
        icon = QLabel("📄")
        icon.setStyleSheet("font-size:18px;")
        icon.setFixedWidth(24)

        # File name
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(
            f"color:{Color.TEXT_PRI}; font-family:{Font.MONO}; font-size:{Font.SIZE_SM}px;"
        )
        lbl_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        lbl_name.setMaximumWidth(240)

        # Size
        lbl_size = QLabel(size)
        lbl_size.setStyleSheet(
            f"color:{Color.TEXT_SEC}; font-size:{Font.SIZE_XS}px;"
        )
        lbl_size.setFixedWidth(54)
        lbl_size.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Modified time
        lbl_time = QLabel(mtime)
        lbl_time.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-family:{Font.MONO}; font-size:{Font.SIZE_XS}px;"
        )
        lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_time.setFixedWidth(148)

        # Download button
        btn = QPushButton("↓  Open")
        btn.setObjectName("btn_download")
        btn.setFixedSize(76, 30)
        btn.clicked.connect(self._open_file)

        root.addWidget(icon)
        root.addWidget(lbl_name, 1)
        root.addWidget(lbl_size)
        root.addWidget(lbl_time)
        root.addWidget(btn)

    def _open_file(self) -> None:
        """Reveal file in the OS file manager."""
        try:
            folder = os.path.dirname(self._path)
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))


class StoragePage(QWidget):
    """
    Screen 4 — Storage / Log Explorer.
    Rebuilds the file list whenever the page becomes visible.
    """

    def __init__(self, logger: SessionLogger, parent=None) -> None:
        super().__init__(parent)
        self._logger      = logger
        self._scroll_lay  = None
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        root.addWidget(self._build_header())
        root.addWidget(self._build_stats_row())

        # Scroll area for file list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(self._scroll)

        self._populate_list()

    def _build_header(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)

        title = QLabel("LOG  STORAGE")
        title.setObjectName("page_header")

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setObjectName("btn_pill")
        refresh_btn.setFixedHeight(30)
        refresh_btn.clicked.connect(self._populate_list)

        lay.addWidget(title)
        lay.addStretch()
        lay.addWidget(refresh_btn)
        return w

    def _build_stats_row(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setFixedHeight(44)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(14, 6, 14, 6)
        lay.setSpacing(24)

        self._lbl_count = QLabel("0 files")
        self._lbl_count.setStyleSheet(
            f"color:{Color.NEON_GREEN}; font-family:{Font.MONO}; font-size:{Font.SIZE_SM}px;"
        )

        self._lbl_dir = QLabel("")
        self._lbl_dir.setStyleSheet(
            f"color:{Color.TEXT_DIM}; font-size:{Font.SIZE_XS}px;"
        )
        self._lbl_dir.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        lay.addWidget(self._lbl_count)
        lay.addWidget(self._lbl_dir, 1)
        return frame

    # ── File list ─────────────────────────────────────────────────────────────

    def _populate_list(self) -> None:
        logs = self._logger.list_logs()

        # Update stats
        self._lbl_count.setText(f"{len(logs)} file{'s' if len(logs) != 1 else ''}")
        self._lbl_dir.setText(f"📁  {SessionLogger.LOG_DIR}")

        # Rebuild container
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        if logs:
            for name, size, mtime, path in logs:
                row = _FileRow(name, size, mtime, path)
                lay.addWidget(row)
        else:
            empty = QLabel("No log files yet.\nUse 'Save Logs' on the Dashboard.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                f"color:{Color.TEXT_DIM}; font-size:{Font.SIZE_MD}px; margin-top:40px;"
            )
            lay.addWidget(empty)

        lay.addStretch()
        self._scroll.setWidget(container)

    # ── Auto-refresh when page becomes visible ────────────────────────────────

    def showEvent(self, event) -> None:   # noqa: N802
        super().showEvent(event)
        self._populate_list()

    # ── Called after a new save ───────────────────────────────────────────────

    def refresh(self, _engine=None) -> None:
        pass  # Storage page self-refreshes via showEvent; no 10 Hz needed
