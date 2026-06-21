from datetime import datetime, timezone

# ANSI/IEEE protection device numbers used as labels, matching
# how real SCADA alarm logs identify the type of protection event.
THRESHOLDS = {
    "overvoltage_trip_v": 450.0,       # ANSI 59
    "undervoltage_trip_v": 380.0,      # ANSI 27
    "overcurrent_instant_a": 500.0,    # ANSI 50 - short-circuit level, trips immediately
    "overcurrent_sustained_a": 350.0,  # ANSI 51 - thermal overload threshold
    "overcurrent_trip_delay_s": 10,    # how long it must persist before tripping
    "freq_low_hz": 49.5,
    "freq_high_hz": 50.5,
}


class ProtectionRelay:
    """Stateful relay: evaluates one reading at a time, remembers
    how long an overcurrent condition has persisted between calls."""

    def __init__(self, thresholds=None):
        self.t = thresholds or THRESHOLDS
        self._overcurrent_since = None

    def evaluate(self, reading, now=None):
        now = now or datetime.now(timezone.utc)
        events = []

        v, i, f = reading["bus_voltage_v"], reading["current_a"], reading["frequency_hz"]

        if v >= self.t["overvoltage_trip_v"]:
            events.append(self._event("TRIP", "59", "Overvoltage", v, "V"))

        if v <= self.t["undervoltage_trip_v"]:
            events.append(self._event("TRIP", "27", "Undervoltage", v, "V"))

        if i >= self.t["overcurrent_instant_a"]:
            events.append(self._event("TRIP", "50", "Instantaneous overcurrent", i, "A"))
        elif i >= self.t["overcurrent_sustained_a"]:
            if self._overcurrent_since is None:
                self._overcurrent_since = now
            elapsed = (now - self._overcurrent_since).total_seconds()
            if elapsed >= self.t["overcurrent_trip_delay_s"]:
                events.append(self._event("TRIP", "51", "Sustained overcurrent (thermal)", i, "A"))
            else:
                events.append(self._event("ALARM", "51", "Overcurrent building", i, "A"))
        else:
            self._overcurrent_since = None  # condition cleared, reset the timer

        if f < self.t["freq_low_hz"] or f > self.t["freq_high_hz"]:
            events.append(self._event("ALARM", "81", "Frequency deviation", f, "Hz"))

        return events

    def _event(self, severity, ansi_code, description, value, unit):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "severity": severity,
            "ansi_code": ansi_code,
            "description": description,
            "value": round(value, 2),
            "unit": unit,
        }


if __name__ == "__main__":
    relay = ProtectionRelay()
    test_readings = [
        {"bus_voltage_v": 413.0, "current_a": 300.0, "frequency_hz": 50.0},  # normal
        {"bus_voltage_v": 413.0, "current_a": 360.0, "frequency_hz": 50.0},  # overload starts
        {"bus_voltage_v": 413.0, "current_a": 360.0, "frequency_hz": 50.0},  # still building
        {"bus_voltage_v": 460.0, "current_a": 300.0, "frequency_hz": 50.0},  # overvoltage
        {"bus_voltage_v": 413.0, "current_a": 550.0, "frequency_hz": 50.0},  # short-circuit level
        {"bus_voltage_v": 413.0, "current_a": 300.0, "frequency_hz": 49.0},  # freq deviation
    ]
    for r in test_readings:
        for event in relay.evaluate(r):
            print(event)
