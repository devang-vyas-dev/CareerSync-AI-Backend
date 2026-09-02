from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth

app = FastAPI(
    title="CareerSync-AI",
    description="This is the Testing of the Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include Auth routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
def root():
    return {"message": "CareerSync AI Backend is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok", "auth": "ready"}