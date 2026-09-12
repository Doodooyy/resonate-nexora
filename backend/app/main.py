from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.core.config import get_settings

# Create database tables
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Explainable AI Resume Shortlisting Engine API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

from app.api import jobs, applications, recruiter, bias, auth
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
app.include_router(jobs.router, prefix=settings.API_V1_STR + "/jobs", tags=["jobs"])
app.include_router(applications.router, prefix=settings.API_V1_STR, tags=["applications"])
app.include_router(recruiter.router, prefix=settings.API_V1_STR, tags=["recruiter"])
app.include_router(bias.router, prefix=settings.API_V1_STR, tags=["bias"])
app.include_router(bias.router, prefix=settings.API_V1_STR, tags=["bias"])
