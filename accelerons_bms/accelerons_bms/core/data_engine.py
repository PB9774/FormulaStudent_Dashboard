"""
core/data_engine.py
────────────────────────────────────────────────────────────────────────────
Accelerons Electric — BMS Data Engine
Simulates UART/CAN data at 10 Hz (drop-in replaceable with real serial I/O).
All public state is read via properties; history stored in bounded deques.
"""

import math
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple


# ── Data containers ──────────────────────────────────────────────────────────

@dataclass
class CellData:
    """Single Li-ion cell telemetry."""
    voltage: float = 3.70
    temperature: float = 25.0


@dataclass
class ModuleData:
    """One BMS module containing CELLS_PER_MODULE cells."""
    CELLS_PER_MODULE: int = field(default=14, init=False, repr=False)
    cells: List[CellData] = field(
        default_factory=lambda: [CellData() for _ in range(14)]
    )


# ── Engine ────────────────────────────────────────────────────────────────────

class DataEngine:
    """
    Core BMS telemetry engine.

    • Simulates 7 modules × 14 cells at 10 Hz.
    • Maintains rolling 30-min history in deques (maxlen=18 000).
    • Replace _simulate() with a real serial/CAN read for production.
    """

    NUM_MODULES       = 7
    CELLS_PER_MODULE  = 14
    MAX_SAMPLES       = 18_000          # 30 min × 10 Hz
    NOMINAL_VOLTAGE   = 3.70
    LOW_VOLTAGE_THR   = 3.40
    HIGH_VOLTAGE_THR  = 3.90

    def __init__(self) -> None:
        self._modules: List[ModuleData] = [
            ModuleData() for _ in range(self.NUM_MODULES)
        ]
        self._speed:         float = 0.0
        self._soc:           float = 87.4
        self._current:       float = 0.0
        self._pack_voltage:  float = 0.0
        self._delta_v:       float = 0.0
        self._elapsed:       float = 0.0
        self._start_time:    float = time.monotonic()

        # Analytics history (relative time, newest = 0)
        self.time_history:    deque = deque(maxlen=self.MAX_SAMPLES)
        self.current_history: deque = deque(maxlen=self.MAX_SAMPLES)
        self.soc_history:     deque = deque(maxlen=self.MAX_SAMPLES)
        self.temp_history:    deque = deque(maxlen=self.MAX_SAMPLES)

    # ── Public API ────────────────────────────────────────────────────────────

    def tick(self) -> None:
        """Advance one 10 Hz tick. Call from a 100 ms QTimer."""
        self._elapsed = time.monotonic() - self._start_time
        self._simulate()
        self._compute_aggregates()
        self._record_history()

    @property
    def modules(self) -> List[ModuleData]:
        return self._modules

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def soc(self) -> float:
        return self._soc

    @property
    def current(self) -> float:
        return self._current

    @property
    def pack_voltage(self) -> float:
        return self._pack_voltage

    @property
    def delta_v(self) -> float:
        return self._delta_v

    @property
    def avg_temperature(self) -> float:
        return self._avg_temp

    def module_avg_voltage(self, idx: int) -> float:
        m = self._modules[idx]
        return sum(c.voltage for c in m.cells) / len(m.cells)

    def module_avg_temp(self, idx: int) -> float:
        m = self._modules[idx]
        return sum(c.temperature for c in m.cells) / len(m.cells)

    def all_voltages(self) -> List[float]:
        return [c.voltage for m in self._modules for c in m.cells]

    def cell_status(self, voltage: float) -> str:
        """Return 'normal', 'low', or 'high' for colour-coding."""
        if voltage < self.LOW_VOLTAGE_THR:
            return "low"
        if voltage > self.HIGH_VOLTAGE_THR:
            return "high"
        return "normal"

    # ── Private helpers ───────────────────────────────────────────────────────

    def _simulate(self) -> None:
        t = self._elapsed

        # Speed — sinusoidal drive cycle
        self._speed = max(0.0, min(
            120.0,
            60 + 35 * math.sin(t * 0.08) + random.gauss(0, 1.5)
        ))

        # SOC — slow drain with regeneration pulses
        drain = 0.003 if self._speed > 10 else 0.0005
        self._soc = max(0.0, self._soc - drain + random.gauss(0, 0.001))

        # Current — proportional to speed with noise
        self._current = self._speed * 0.85 + random.gauss(0, 2)

        # Cell voltages and temperatures
        for m_idx, module in enumerate(self._modules):
            for c_idx, cell in enumerate(module.cells):
                phase = t * 0.06 + m_idx * 0.4 + c_idx * 0.15
                cell.voltage = (
                    self.NOMINAL_VOLTAGE
                    + 0.08 * math.sin(phase)
                    + random.gauss(0, 0.008)
                )
                # Inject rare anomalies (< 0.3 % per cell per tick)
                if random.random() < 0.003:
                    cell.voltage = random.choice([3.25, 4.05])

                cell.temperature = (
                    27
                    + 6 * math.sin(t * 0.02 + m_idx * 0.6)
                    + random.gauss(0, 0.4)
                )

    def _compute_aggregates(self) -> None:
        voltages = self.all_voltages()
        temps = [c.temperature for m in self._modules for c in m.cells]

        self._pack_voltage = sum(voltages)
        self._delta_v      = max(voltages) - min(voltages)
        self._avg_temp     = sum(temps) / len(temps)

    def _record_history(self) -> None:
        self.time_history.append(self._elapsed)    # positive, always growing
        self.current_history.append(self._current)
        self.soc_history.append(self._soc)
        self.temp_history.append(self._avg_temp)
