"""
core/logger.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — Session Logger
Writes BMS snapshots to timestamped CSV files in ./logs/.
"""

import csv
import os
import time
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.data_engine import DataEngine


class SessionLogger:
    """
    Saves BMS snapshots to CSV.

    Usage:
        logger = SessionLogger(engine)
        path = logger.save_snapshot()   # returns file path
        files = logger.list_logs()      # returns list of (path, size, mtime)
    """

    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

    def __init__(self, engine: "DataEngine") -> None:
        self._engine = engine
        os.makedirs(self.LOG_DIR, exist_ok=True)

    def save_snapshot(self) -> str:
        """Write current history buffers to a CSV file. Returns file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bms_log_{timestamp}.csv"
        filepath = os.path.join(self.LOG_DIR, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "relative_time_s", "current_A", "soc_pct", "avg_temp_C"
            ])
            times    = list(self._engine.time_history)
            currents = list(self._engine.current_history)
            socs     = list(self._engine.soc_history)
            temps    = list(self._engine.temp_history)

            for row in zip(times, currents, socs, temps):
                writer.writerow([f"{v:.4f}" for v in row])

        return filepath

    def list_logs(self) -> list:
        """Return list of (filename, size_str, datetime_str) for each log."""
        result = []
        try:
            entries = sorted(os.listdir(self.LOG_DIR), reverse=True)
            for name in entries:
                if not name.endswith(".csv"):
                    continue
                path = os.path.join(self.LOG_DIR, name)
                stat = os.stat(path)
                size_kb = stat.st_size / 1024
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d  %H:%M:%S"
                )
                result.append((name, f"{size_kb:.1f} KB", mtime, path))
        except FileNotFoundError:
            pass
        return result
