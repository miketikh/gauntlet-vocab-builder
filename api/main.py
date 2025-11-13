"""
Vocab Builder FastAPI Backend
Main application entry point with SQLModel integration
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from models.database import Educator, Student, EducatorPublic
from services.database import get_session, init_db
from routers import auth, s3, students, documents

app = FastAPI(
    title="Vocab Builder API",
    description="AI-powered vocabulary recommendation engine for middle school students",
    version="0.1.0",
    openapi_url="/openapi.json",  # Explicit OpenAPI JSON endpoint
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",  # Alternative dev port
    ],
    allow_credentials=True,  # Required for authenticated requests
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],  # Explicitly allow Authorization header
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup
    Note: In production, use Alembic migrations instead
    """
    print("Starting up Vocab Builder API...")
    # Uncomment to auto-create tables (dev only)
    # init_db()
    print("API ready!")


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(s3.router, prefix="/api/s3", tags=["S3 Document Storage"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vocab Builder API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vocab-builder-api",
        "version": "0.1.0",
        "database": "connected"
    }


@app.get("/api/educators", response_model=list[EducatorPublic])
async def get_educators(
    session: Session = Depends(get_session),
    limit: int = 10
):
    """
    Example endpoint: Get all educators (limited)

    This demonstrates SQLModel integration with FastAPI.
    In production, this would be protected and filtered by auth.
    """
    statement = select(Educator).limit(limit)
    educators = session.exec(statement).all()
    return educators


@app.get("/api/educators/{educator_id}/students")
async def get_educator_students(
    educator_id: int,
    session: Session = Depends(get_session)
):
    """
    Example endpoint: Get all students for an educator

    In production, this would verify JWT and ensure educator owns these students.
    """
    statement = select(Student).where(Student.educator_id == educator_id)
    students = session.exec(statement).all()
    return students
