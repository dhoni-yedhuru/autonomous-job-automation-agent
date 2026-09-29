from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Candidate, Job

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

@app.put("/candidates/{candidate_id}")
def update_candidate(
    candidate_id: int,
    candidate: CandidateCreate,
    db: Session = Depends(get_db)
):
    existing_candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if not existing_candidate:
        return {"error": "Candidate not found"}

    existing_candidate.full_name = candidate.full_name
    existing_candidate.email = candidate.email
    existing_candidate.phone = candidate.phone
    existing_candidate.location = candidate.location
    existing_candidate.experience_years = candidate.experience_years
    existing_candidate.target_titles = candidate.target_titles
    existing_candidate.skills = candidate.skills
    existing_candidate.master_resume = candidate.master_resume

    db.commit()
    db.refresh(existing_candidate)

    return existing_candidate

class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    job_url: str | None = None
    source: str | None = None
    description: str | None = None
    required_skills: str | None = None
    salary: str | None = None
    work_mode: str | None = None
    posted_date: str | None = None
    status: str = "new"
    match_score: int = 0


@app.post("/jobs")
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    new_job = Job(**job.model_dump())

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@app.get("/jobs")
def get_jobs(
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).order_by(Job.id.desc()).all()

    return jobs