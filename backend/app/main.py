from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Candidate, Job
from matching import calculate_match_score
from job_discovery import search_jobs

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

@app.post("/jobs/discover")
def discover_jobs(
    db: Session = Depends(get_db)
):
    discovered_jobs = search_jobs()

    created_jobs = []

    for job_data in discovered_jobs:
        existing_job = db.query(Job).filter(
            Job.job_url == job_data["job_url"]
        ).first()

        if existing_job:
            continue

        new_job = Job(
            title=job_data["title"],
            company=job_data["company"],
            location=job_data["location"],
            job_url=job_data["job_url"],
            source=job_data["source"],
            required_skills=job_data["required_skills"],
            status="new"
        )

        db.add(new_job)
        created_jobs.append(new_job)

    db.commit()

    for job in created_jobs:
        db.refresh(job)

    return {
        "message": "Job discovery completed",
        "new_jobs": len(created_jobs),
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source": job.source,
                "job_url": job.job_url,
                "required_skills": job.required_skills,
                "status": job.status
            }
            for job in created_jobs
        ]
    }
    
@app.get("/jobs")
def get_jobs(
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).order_by(
        Candidate.id.desc()
    ).first()

    jobs = db.query(Job).order_by(Job.id.desc()).all()

    if candidate:
        for job in jobs:
            job.match_score = calculate_match_score(
                candidate.skills,
                job.required_skills
            )

        db.commit()

    return [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_url": job.job_url,
            "source": job.source,
            "description": job.description,
            "required_skills": job.required_skills,
            "salary": job.salary,
            "work_mode": job.work_mode,
            "posted_date": job.posted_date,
            "status": job.status,
            "match_score": job.match_score
        }
        for job in jobs
    ]

@app.get("/jobs/{job_id}/match/{candidate_id}")
def match_job(
    job_id: int,
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if not candidate:
        return {"error": "Candidate not found"}

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return {"error": "Job not found"}

    score = calculate_match_score(
        candidate.skills,
        job.required_skills
    )

    job.match_score = score

    db.commit()
    db.refresh(job)

    return {
        "candidate_id": candidate.id,
        "job_id": job.id,
        "job_title": job.title,
        "candidate_skills": candidate.skills,
        "required_skills": job.required_skills,
        "match_score": score
    }