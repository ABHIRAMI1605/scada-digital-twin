import json
import os

FAULT_FILE = os.path.join("data", "fault_command.json")


def write_fault(fault_type):
    os.makedirs("data", exist_ok=True)
    with open(FAULT_FILE, "w") as f:
        json.dump({"fault": fault_type}, f)


def read_fault():
    if not os.path.exists(FAULT_FILE):
        return None
    try:
        with open(FAULT_FILE) as f:
            return json.load(f).get("fault")
    except (json.JSONDecodeError, OSError):
        # File was being written by the other process at the exact
        # moment we tried to read it — just skip this cycle, harmless.
        return None
