import csv
import os
from collections import deque
from datetime import datetime, timezone

from simulation.plant_model import Plant
from protection.fault_logic import ProtectionRelay

READINGS_CSV = os.path.join("data", "readings.csv")
ALARMS_CSV = os.path.join("data", "alarms.csv")

READING_FIELDS = [
    "timestamp", "sim_time_s", "bus_voltage_v", "frequency_hz",
    "total_kw", "total_kvar", "total_kva", "power_factor", "current_a",
    "fault_injected",
]
ALARM_FIELDS = ["timestamp", "severity", "ansi_code", "description", "value", "unit"]


class SimulationState:
    def recent_readings(self, n=60):
        return list(self.readings)[-n:]
    def __init__(self, history_size=120):
        self.plant = Plant()
        self.relay = ProtectionRelay()
        self.sim_time = 0
        self.readings = deque(maxlen=history_size)
        self.alarms = deque(maxlen=100)
        self._ensure_csv(READINGS_CSV, READING_FIELDS)
        self._ensure_csv(ALARMS_CSV, ALARM_FIELDS)

    def _ensure_csv(self, path, fields):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", newline="") as f:
                csv.DictWriter(f, fieldnames=fields).writeheader()

    def step(self, sim_time_step=30):
        reading = self.plant.step(self.sim_time)
        reading["sim_time_s"] = reading.pop("time_s")
        reading["timestamp"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.readings.append(reading)
        self._log_csv(READINGS_CSV, READING_FIELDS, reading)

        new_alarms = self.relay.evaluate(reading)
        for event in new_alarms:
            self.alarms.append(event)
            self._log_csv(ALARMS_CSV, ALARM_FIELDS, event)

        self.sim_time += sim_time_step
        return reading, new_alarms

    def _log_csv(self, path, fields, row):
        with open(path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=fields).writerow({k: row.get(k) for k in fields})

    def inject_fault(self, fault_type):
        self.plant.set_fault(fault_type)

    def clear_fault(self):
        self.plant.set_fault(None)

    def latest_reading(self):
        return self.readings[-1] if self.readings else None

    def recent_alarms(self, n=50):
        return list(self.alarms)[-n:][::-1]
