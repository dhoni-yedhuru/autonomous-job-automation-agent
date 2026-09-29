from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Candidate

app = FastAPI(title="Autonomous Job Automation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CandidateCreate(BaseModel):
    full_name: str
    email: str
    phone: str | None = None
    location: str | None = None
    experience_years: int = 0
    target_titles: str | None = None
    skills: str | None = None
    master_resume: str | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "Job Automation Agent API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/candidates")
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    new_candidate = Candidate(**candidate.model_dump())

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return new_candidate

@app.get("/candidates/{candidate_id}")
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if not candidate:
        return {"error": "Candidate not found"}

    return candidate