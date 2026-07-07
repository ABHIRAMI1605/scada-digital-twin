# SCADA Digital Twin — Industrial Power Plant

A full-stack digital twin that simulates the monitoring and control of an industrial power plant, modeled on real SCADA (Supervisory Control and Data Acquisition) system architecture. Built to explore how acquisition, control, protection, and simulation layers work together in an industrial automation environment, with a live web dashboard on top.

## Overview

The project is organized into modules that mirror a real SCADA stack:

| Module | Responsibility |
|---|---|
| `simulation/` | Models plant-level process behavior and generates realistic sensor data over time |
| `acquisition/` | Collects and pre-processes simulated sensor/telemetry data from the plant model |
| `backend/` | Python REST services that process, store, and expose acquisition and control data |
| `control/` | Control logic for regulating plant parameters based on incoming telemetry |
| `protection/` | Fault detection and safety-interlock logic, mirroring real industrial protection schemes |
| `dashboard/` `frontend/` | Web dashboard for visualizing live plant telemetry, control states, and alerts |
| `data/` | Sample/generated datasets used by the simulation and acquisition layers |

## Tech Stack

- **Backend & Simulation:** Python
- **Frontend/Dashboard:** JavaScript, HTML, CSS
- **Data:** File/DB-based storage for telemetry and simulation output (see `requirements.txt` for dependencies)

## Why this project

Most student IoT/embedded projects stop at a single sensor-to-dashboard pipeline. This one is structured the way an actual industrial SCADA system is layered — separating acquisition, control, and protection concerns — to get closer to how monitoring and safety systems are designed in real power plants.

## Getting Started

```bash
git clone https://github.com/ABHIRAMI1605/scada-digital-twin.git
cd scada-digital-twin
pip install -r requirements.txt

# Run the simulation layer
python simulation/<entry_point>.py

# Start the backend
python backend/<entry_point>.py

# Open the dashboard
cd dashboard   # or frontend/
```

## Roadmap

- [ ] Add unit tests for control and protection logic
- [ ] Deploy backend + dashboard for a live demo link
- [ ] Add architecture diagram
- [ ] Expand protection module with additional fault scenarios

## Author

**Abhirami S** — Final-year EEE student, Sri Sairam Institute of Technology
[LinkedIn](https://www.linkedin.com/in/abhirami-s-b20606294/) · [GitHub](https://github.com/ABHIRAMI1605)
