import csv
import os
import time
from datetime import datetime, timezone

from simulation.plant_model import Plant
from protection.fault_logic import ProtectionRelay
from control.fault_control import read_fault

CSV_PATH = os.path.join("data", "readings.csv")
ALARMS_CSV_PATH = os.path.join("data", "alarms.csv")
SAMPLE_INTERVAL_S = 2
SIM_TIME_STEP_S = 30

FIELDNAMES = [
    "timestamp", "sim_time_s", "bus_voltage_v", "frequency_hz",
    "total_kw", "total_kvar", "total_kva", "power_factor", "current_a",
    "fault_injected",
]
ALARM_FIELDNAMES = ["timestamp", "severity", "ansi_code", "description", "value", "unit"]


def ensure_csv_header(path, fieldnames):
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=fieldnames).writeheader()


def log_reading(reading):
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sim_time_s": reading["time_s"],
        **{k: reading[k] for k in FIELDNAMES if k in reading},
    }
    with open(CSV_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDNAMES).writerow(row)
        f.flush()


def log_alarm(event):
    with open(ALARMS_CSV_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=ALARM_FIELDNAMES).writerow(event)
        f.flush()


def run_acquisition_loop():
    ensure_csv_header(CSV_PATH, FIELDNAMES)
    ensure_csv_header(ALARMS_CSV_PATH, ALARM_FIELDNAMES)

    plant = Plant()
    relay = ProtectionRelay()
    sim_time = 0
    last_fault = None

    print(f"Logging to {CSV_PATH} every {SAMPLE_INTERVAL_S}s (Ctrl+C to stop)...")
    try:
        while True:
            current_fault = read_fault()
            if current_fault != last_fault:
                print(f"*** Fault state changed: {last_fault} -> {current_fault} ***")
                last_fault = current_fault
            plant.set_fault(current_fault)

            reading = plant.step(sim_time)
            log_reading(reading)
            print(reading)

            for event in relay.evaluate(reading):
                log_alarm(event)
                print(f"  >> {event['severity']} [{event['ansi_code']}] {event['description']}")

            sim_time += SIM_TIME_STEP_S
            time.sleep(SAMPLE_INTERVAL_S)
    except KeyboardInterrupt:
        print("\nAcquisition stopped.")


if __name__ == "__main__":
    run_acquisition_loop()
