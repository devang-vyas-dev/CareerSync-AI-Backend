from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, resume
from app.api.v1 import roadmap, internships

app = FastAPI(
    title="CareerSync-AI",
    description="This is the Testing of the Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://careersync-ai-blond.vercel.app",
        "https://careersync-ai-blond.vercel.app/",
        "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include Auth routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["resume"])
app.include_router(roadmap.router, prefix="/api/v1/roadmap", tags=["Roadmap"])
app.include_router(internships.router, prefix="/api/v1/internship", tags=["Internships"])

@app.get("/")
async def root():
    return {"message": "CareerSync AI Backend is running 🚀"}

@app.get("/health")
async def health():
    return {"status": "ok", "auth": "ready"}
