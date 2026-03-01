"""
main.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — BMS Monitor
Entry point.  Run with:  python main.py

Requirements:
    pip install PyQt6 pyqtgraph numpy
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QFont

from ui.main_window              import MainWindow
from ui.widgets.splash_screen    import SplashScreen

# Assets directory — user can drop logo.png here
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Accelerons Electric BMS")
    app.setApplicationDisplayName("Accelerons Electric")
    app.setOrganizationName("Accelerons Electric Racing")

    default_font = QFont("Roboto", 11)
    app.setFont(default_font)

    # Build main window first (hidden)
    window = MainWindow()

    # Show splash — when it finishes animating, reveal main window
    splash = SplashScreen(assets_dir=ASSETS_DIR)

    def _on_splash_done():
        window.show()
        splash.deleteLater()

    splash.done.connect(_on_splash_done)
    splash.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
