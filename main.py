from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the OFC NMS API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "OFC NMS API"}
