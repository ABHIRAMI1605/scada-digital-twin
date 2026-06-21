import numpy as np

GRID_VOLTAGE = 415.0
GRID_FREQUENCY = 50.0


class Transformer:
    def __init__(self, primary_kv=11.0, secondary_v=415.0, rated_kva=500):
        self.primary_kv = primary_kv
        self.secondary_v = secondary_v
        self.rated_kva = rated_kva
        self.turns_ratio = (primary_kv * 1000) / secondary_v

    def secondary_voltage(self, loading_fraction):
        droop = 0.02 * min(loading_fraction, 1.5)
        return self.secondary_v * (1 - droop)


class Load:
    def __init__(self, name, rated_kw, power_factor=1.0, lagging=True):
        self.name = name
        self.rated_kw = rated_kw
        self.power_factor = power_factor
        self.lagging = lagging
        self.duty = 1.0

    def real_power_kw(self):
        return self.rated_kw * self.duty

    def reactive_power_kvar(self):
        if self.power_factor >= 0.999:
            return 0.0
        phi = np.arccos(self.power_factor)
        q = self.real_power_kw() * np.tan(phi)
        return q if self.lagging else -q

    def apparent_power_kva(self):
        p, q = self.real_power_kw(), self.reactive_power_kvar()
        return np.sqrt(p**2 + q**2)


class Bus:
    def __init__(self, voltage=GRID_VOLTAGE, frequency=GRID_FREQUENCY):
        self.voltage = voltage
        self.frequency = frequency
        self.loads = []

    def add_load(self, load):
        self.loads.append(load)

    def total_real_power_kw(self):
        return sum(l.real_power_kw() for l in self.loads)

    def total_reactive_power_kvar(self):
        return sum(l.reactive_power_kvar() for l in self.loads)

    def total_apparent_power_kva(self):
        p, q = self.total_real_power_kw(), self.total_reactive_power_kvar()
        return np.sqrt(p**2 + q**2)

    def power_factor(self):
        s = self.total_apparent_power_kva()
        return self.total_real_power_kw() / s if s > 0 else 1.0

    def total_current_amps(self):
        s_va = self.total_apparent_power_kva() * 1000
        return s_va / self.voltage if self.voltage > 0 else 0.0


class Plant:
    def __init__(self):
        self.transformer = Transformer(primary_kv=11.0, secondary_v=415.0, rated_kva=500)
        self.bus = Bus()

        self.motor = Load("Motor-1", rated_kw=75, power_factor=0.85, lagging=True)
        self.lighting = Load("Lighting", rated_kw=20, power_factor=1.0)
        self.hvac = Load("HVAC", rated_kw=40, power_factor=0.9, lagging=True)

        for load in (self.motor, self.lighting, self.hvac):
            self.bus.add_load(load)

        # None = normal operation. "overload" or "short_circuit" forces
        # the motor to a fixed abnormal duty, overriding the sine wave below.
        self.fault_override = None

    def set_fault(self, fault_type):
        self.fault_override = fault_type  # None, "overload", or "short_circuit"

    def step(self, t_seconds):
        if self.fault_override == "overload":
            self.motor.duty = 1.3       # ~425A — lands between the 51 and 50 thresholds
        elif self.fault_override == "short_circuit":
            self.motor.duty = 2.5       # ~600-680A — clears the 50 instantaneous threshold
        else:
            self.motor.duty = 0.7 + 0.1 * np.sin(2 * np.pi * t_seconds / 300)

        self.lighting.duty = 1.0
        self.hvac.duty = 0.3 + 0.7 * (np.sin(2 * np.pi * t_seconds / 600) > 0)

        loading_fraction = self.bus.total_apparent_power_kva() / self.transformer.rated_kva
        self.bus.voltage = self.transformer.secondary_voltage(loading_fraction)

        return {
            "time_s": t_seconds,
            "bus_voltage_v": round(self.bus.voltage, 2),
            "frequency_hz": self.bus.frequency,
            "total_kw": round(self.bus.total_real_power_kw(), 2),
            "total_kvar": round(self.bus.total_reactive_power_kvar(), 2),
            "total_kva": round(self.bus.total_apparent_power_kva(), 2),
            "power_factor": round(self.bus.power_factor(), 3),
            "current_a": round(self.bus.total_current_amps(), 2),
            "fault_injected": self.fault_override or "none",
        }


if __name__ == "__main__":
    plant = Plant()
    for t in range(0, 10):
        print(plant.step(t))
