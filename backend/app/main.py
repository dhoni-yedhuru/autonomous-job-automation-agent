import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Candidate, Job, Application
from matching import calculate_match_score, analyze_match
from job_discovery import search_jobs
from job_analysis import analyze_job
from resume_generator import generate_resume_content
from latex_resume import generate_latex_resume

from application_automation import open_application_page

from fastapi.responses import Response

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

class OpenJobRequest(BaseModel):
    job_url: str


@app.post("/automation/open-job")
def open_job_for_application(request: OpenJobRequest):
    open_application_page(request.job_url)

    return {
        "message": "Job application page opened successfully."
    }

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
    
    
class ApplicationCreate(BaseModel):
    candidate_id: int
    job_id: int
    status: str = "saved"
    applied_date: str | None = None
    notes: str | None = None

@app.post("/applications")
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    existing_application = db.query(Application).filter(
        Application.candidate_id == application.candidate_id,
        Application.job_id == application.job_id
    ).first()

    if existing_application:
        return {
            "error": "Application already exists",
            "application_id": existing_application.id
        }

    new_application = Application(
        **application.model_dump()
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application

@app.get("/applications")
def get_applications(
    db: Session = Depends(get_db)
):
    applications = db.query(Application).order_by(
        Application.id.desc()
    ).all()

    return [
        {
            "id": application.id,
            "candidate_id": application.candidate_id,
            "job_id": application.job_id,
            "status": application.status,
            "applied_date": application.applied_date,
            "notes": application.notes,
        }
        for application in applications
    ]

class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: str | None = None


@app.put("/applications/{application_id}")
def update_application(
    application_id: int,
    application: ApplicationStatusUpdate,
    db: Session = Depends(get_db)
):
    existing_application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not existing_application:
        return {"error": "Application not found"}

    existing_application.status = application.status
    existing_application.notes = application.notes

    db.commit()
    db.refresh(existing_application)

    return existing_application


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
    
@app.get("/jobs/{job_id}/analysis")
def get_job_analysis(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return {"error": "Job not found"}

    job_data = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "work_mode": job.work_mode,
        "required_skills": job.required_skills,
        "description": job.description,
    }

    return analyze_job(job_data)

@app.get("/jobs/{job_id}/resume/{candidate_id}")
def generate_job_resume(
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

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "skills": candidate.skills,
        "master_resume": candidate.master_resume,
    }

    job_data = {
        "title": job.title,
        "company": job.company,
        "required_skills": job.required_skills,
    }

    return generate_resume_content(
        candidate_data,
        job_data
    )
    
@app.get("/jobs/{job_id}/latex-resume/{candidate_id}")
def generate_job_latex_resume(
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

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "skills": candidate.skills,
        "master_resume": candidate.master_resume,
    }

    job_data = {
        "title": job.title,
        "company": job.company,
    }

    latex = generate_latex_resume(
        candidate_data,
        job_data
    )

    return {
        "job_id": job.id,
        "candidate_id": candidate.id,
        "job_title": job.title,
        "company": job.company,
        "latex": latex,
    }
    
@app.get("/jobs/{job_id}/pdf-resume/{candidate_id}")
def generate_job_pdf_resume(
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

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "skills": candidate.skills,
        "master_resume": candidate.master_resume,
    }

    job_data = {
        "title": job.title,
        "company": job.company,
    }

    latex = generate_latex_resume(
        candidate_data,
        job_data
    )

    from latex_resume import compile_latex_to_pdf

    pdf_content = compile_latex_to_pdf(latex)

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{job.title.replace(" ", "_")}_Resume.pdf"'
            )
        }
    )
    
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

    match_result = analyze_match(
        candidate.skills,
        job.required_skills
    )

    job.match_score = match_result["match_score"]

    db.commit()
    db.refresh(job)

    return {
        "candidate_id": candidate.id,
        "job_id": job.id,
        "job_title": job.title,
        "candidate_skills": candidate.skills,
        "required_skills": job.required_skills,
        **match_result
    }