from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import segments, alarms, work_orders, dashboard
from app.websocket_manager import manager

# Create tables if they don't exist
Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="OFC NMS API",
    description="API for Indigenous GIS based OFC Network Management System",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(segments.router)
app.include_router(alarms.router)
app.include_router(work_orders.router)
app.include_router(dashboard.router)

@app.websocket("/api/ws/alarms")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't really expect clients to send messages right now, but we must listen to keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {"message": "Welcome to the OFC NMS API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "OFC NMS API"}
