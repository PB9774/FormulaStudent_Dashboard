"""
ui/main_window.py
Accelerons Electric — Main Window (5 pages)
"""
from PyQt6.QtCore    import QTimer
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMessageBox

from core.data_engine import DataEngine
from core.logger      import SessionLogger

from ui.styles.theme           import MASTER_QSS
from ui.widgets.nav_bar        import NavBar
from ui.pages.dashboard_page   import DashboardPage
from ui.pages.heatmap_page     import HeatmapPage
from ui.pages.analytics_page   import AnalyticsPage
from ui.pages.timer_page       import TimerPage
from ui.pages.storage_page     import StoragePage


class MainWindow(QMainWindow):
    TICK_MS = 100  # 10 Hz

    def __init__(self) -> None:
        super().__init__()
        self._engine  = DataEngine()
        self._logger  = SessionLogger(self._engine)
        self._pages   = []
        self._current = 0
        self._setup_window()
        self._build_ui()
        self._start_engine()

    def _setup_window(self) -> None:
        self.setWindowTitle("Accelerons Electric — BMS Monitor")
        self.setMinimumSize(900, 560)
        self.resize(1100, 660)
        self.setStyleSheet(MASTER_QSS)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedWidget()
        self._dashboard  = DashboardPage(on_save_logs=self._save_logs)
        self._heatmap    = HeatmapPage(self._engine)
        self._analytics  = AnalyticsPage(self._engine)
        self._timer_page = TimerPage()
        self._storage    = StoragePage(self._logger)

        self._pages = [
            self._dashboard,
            self._heatmap,
            self._analytics,
            self._timer_page,
            self._storage,
        ]
        for page in self._pages:
            self._stack.addWidget(page)

        self._nav = NavBar()
        self._nav.page_changed.connect(self._switch_page)

        root.addWidget(self._stack, 1)
        root.addWidget(self._nav)

    def _switch_page(self, idx: int) -> None:
        self._current = idx
        self._stack.setCurrentIndex(idx)

    def _start_engine(self) -> None:
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    def _tick(self) -> None:
        self._engine.tick()
        self._pages[self._current].refresh(self._engine)

    def _save_logs(self) -> None:
        try:
            path = self._logger.save_snapshot()
            QMessageBox.information(self, "Log Saved",
                f"Session data saved.\n\n{path}")
            self._storage.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))

    def closeEvent(self, event) -> None:
        self._timer.stop()
        super().closeEvent(event)
