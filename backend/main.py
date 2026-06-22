import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.state import SimulationState

POLL_INTERVAL_S = 2
SIM_TIME_STEP_S = 30

state = SimulationState()
start_time = datetime.now(timezone.utc)


class ConnectionManager:
    """Tracks every connected WebSocket client and pushes data to all of
    them at once. A dead connection during broadcast just gets dropped —
    we don't want one disconnected client to crash the whole loop."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, payload: dict):
        stale = []
        for connection in self.active:
            try:
                await connection.send_json(payload)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


manager = ConnectionManager()


async def simulation_loop():
    while True:
        reading, new_alarms = state.step(sim_time_step=SIM_TIME_STEP_S)
        await manager.broadcast({"reading": reading, "new_alarms": new_alarms})
        await asyncio.sleep(POLL_INTERVAL_S)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()


app = FastAPI(title="Plant SCADA Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_origin_regex=r"https://scada-digital-twin.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


class FaultRequest(BaseModel):
    fault_type: str  # "overload" or "short_circuit"


@app.get("/status")
def get_status():
    uptime_s = (datetime.now(timezone.utc) - start_time).total_seconds()
    return {
        "status": "RUNNING",
        "uptime_s": round(uptime_s, 1),
        "fault_injected": state.plant.fault_override or "none",
        "sim_time_s": state.sim_time,
    }


@app.get("/readings/latest")
def get_latest_reading():
    reading = state.latest_reading()
    if reading is None:
        raise HTTPException(status_code=503, detail="No readings yet — simulation just started")
    return reading


@app.get("/readings/history")
def get_reading_history(limit: int = 60):
    return state.recent_readings(n=limit)


@app.get("/alarms")
def get_alarms(limit: int = 50):
    return state.recent_alarms(n=limit)


@app.post("/fault/inject")
def inject_fault(req: FaultRequest):
    if req.fault_type not in ("overload", "short_circuit"):
        raise HTTPException(status_code=400, detail="fault_type must be 'overload' or 'short_circuit'")
    state.inject_fault(req.fault_type)
    return {"message": f"Fault '{req.fault_type}' injected", "fault_injected": req.fault_type}


@app.post("/fault/clear")
def clear_fault():
    state.clear_fault()
    return {"message": "Fault cleared", "fault_injected": "none"}


@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect the client to send anything — this just
            # blocks until the client disconnects, which is what raises
            # WebSocketDisconnect below. All actual data goes out via
            # manager.broadcast() from the simulation loop, not from here.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)