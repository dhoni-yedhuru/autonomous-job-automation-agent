import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Candidate, Job, Application, Recruiter, Outreach, KnowledgeFact
from matching import calculate_match_score, analyze_match
from job_discovery import search_jobs
from job_analysis import analyze_job
from resume_generator import generate_resume_content
from latex_resume import generate_latex_resume

from application_automation import apply_to_mock_portal
from mock_portal import router as mock_portal_router
from datetime import datetime

from outreach import generate_outreach_email

from agent import run_agent

from pydantic import BaseModel

from fastapi.responses import Response

app = FastAPI(title="Autonomous Job Automation Agent")

app.include_router(mock_portal_router)

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

class RecruiterCreate(BaseModel):
    name: str
    company: str | None = None
    role: str | None = None
    email: str | None = None
    profile_url: str | None = None
    source: str | None = None
    status: str = "discovered"
    notes: str | None = None
    
class KnowledgeFactCreate(BaseModel):
    candidate_id: int
    category: str
    fact: str
    source: str | None = None
    verified: int = 1
    notes: str | None = None
    
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


@app.post("/automation/apply-mock/{job_id}")
def apply_mock_application(
    job_id: int,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.id == 3
    ).first()

    if not candidate:
        return {"error": "Candidate not found"}

    existing_application = db.query(Application).filter(
        Application.candidate_id == candidate.id,
        Application.job_id == job_id
    ).first()

    if existing_application:
        return {
            "message": "Application already exists",
            "application_id": existing_application.id,
            "status": existing_application.status,
        }

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "experience_years": candidate.experience_years,
        "skills": candidate.skills,
    }

    apply_to_mock_portal(
        job_id,
        candidate_data
    )

    new_application = Application(
        candidate_id=candidate.id,
        job_id=job_id,
        status="applied",
        applied_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        notes="Submitted through mock application portal",
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return {
        "message": "Application submitted and saved successfully",
        "application_id": new_application.id,
        "candidate_id": candidate.id,
        "job_id": job_id,
        "status": new_application.status,
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
    
    
@app.post("/recruiters")
def create_recruiter(
    data: RecruiterCreate,
    db: Session = Depends(get_db)
):
    recruiter = Recruiter(**data.model_dump())

    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)

    return recruiter


@app.get("/recruiters")
def get_recruiters(
    db: Session = Depends(get_db)
):
    return db.query(Recruiter).order_by(
        Recruiter.id.desc()
    ).all()

@app.post("/outreach/generate")
def generate_outreach(
    candidate_id: int,
    recruiter_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    recruiter = db.query(Recruiter).filter(
        Recruiter.id == recruiter_id
    ).first()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not candidate:
        return {"error": "Candidate not found"}

    if not recruiter:
        return {"error": "Recruiter not found"}

    if not job:
        return {"error": "Job not found"}

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "skills": candidate.skills,
        "master_resume": candidate.master_resume,
    }

    recruiter_data = {
        "name": recruiter.name,
        "company": recruiter.company,
        "email": recruiter.email,
        "role": recruiter.role,
    }

    job_data = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "required_skills": job.required_skills,
    }

    return generate_outreach_email(
        candidate_data,
        recruiter_data,
        job_data
    )
    
@app.post("/outreach/save")
def save_outreach(
    candidate_id: int,
    recruiter_id: int,
    job_id: int,
    subject: str,
    body: str,
    db: Session = Depends(get_db)
):
    outreach = Outreach(
        candidate_id=candidate_id,
        recruiter_id=recruiter_id,
        job_id=job_id,
        subject=subject,
        body=body,
        status="draft"
    )

    db.add(outreach)
    db.commit()
    db.refresh(outreach)

    return {
        "message": "Outreach saved successfully",
        "outreach_id": outreach.id,
        "status": outreach.status
    }


@app.patch("/outreach/{outreach_id}/status")
def update_outreach_status(
    outreach_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    outreach = db.query(Outreach).filter(
        Outreach.id == outreach_id
    ).first()

    if not outreach:
        return {"error": "Outreach not found"}

    allowed_statuses = {
        "draft",
        "sent",
        "delivered",
        "replied",
        "positive",
        "negative",
        "follow_up"
    }

    if status not in allowed_statuses:
        return {
            "error": "Invalid status",
            "allowed_statuses": list(allowed_statuses)
        }

    outreach.status = status

    if status == "sent":
        outreach.sent_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    if status == "replied":
        outreach.replied_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    db.commit()
    db.refresh(outreach)

    return {
        "message": "Outreach status updated",
        "outreach_id": outreach.id,
        "status": outreach.status
    }


@app.get("/outreach")
def get_outreach(
    db: Session = Depends(get_db)
):
    return db.query(Outreach).order_by(
        Outreach.id.desc()
    ).all()
    
@app.post("/knowledge")
def create_knowledge_fact(
    data: KnowledgeFactCreate,
    db: Session = Depends(get_db)
):
    fact = KnowledgeFact(**data.model_dump())

    db.add(fact)
    db.commit()
    db.refresh(fact)

    return fact


@app.get("/knowledge/{candidate_id}")
def get_knowledge_facts(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    return db.query(KnowledgeFact).filter(
        KnowledgeFact.candidate_id == candidate_id
    ).order_by(
        KnowledgeFact.id.desc()
    ).all()
    
@app.post("/agent/run")
def run_autonomous_agent(
    candidate_id: int,
    recruiter_id: int | None = None,
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if not candidate:
        return {"error": "Candidate not found"}

    recruiter = None
    recruiter_data = None

    if recruiter_id:
        recruiter = db.query(Recruiter).filter(
            Recruiter.id == recruiter_id
        ).first()

        if recruiter:
            recruiter_data = {
                "name": recruiter.name,
                "company": recruiter.company,
                "role": recruiter.role,
                "email": recruiter.email,
                "profile_url": recruiter.profile_url,
            }

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "experience_years": candidate.experience_years,
        "skills": candidate.skills,
        "master_resume": candidate.master_resume,
    }

    # Get jobs directly from database
    db_jobs = db.query(Job).order_by(Job.id.desc()).all()

    saved_applications = 0
    submitted_applications = 0
    skipped_applications = 0
    saved_outreach = 0
    errors = []
    results = []

    for job in db_jobs:

        job_data = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "source": job.source,
            "job_url": job.job_url,
            "required_skills": job.required_skills,
            "description": job.description,
            "work_mode": job.work_mode,
            "salary": job.salary,
            "posted_date": job.posted_date,
        }

        analysis = analyze_job(job_data)

        match = analyze_match(
            candidate.skills or "",
            job.required_skills or ""
        )

        resume = generate_resume_content(
            candidate_data,
            job_data
        )

        outreach_data = None

        if recruiter:
            recruiter_data_for_email = {
                "name": recruiter.name,
                "company": recruiter.company,
                "role": recruiter.role,
                "email": recruiter.email,
            }

            outreach_data = generate_outreach_email(
                candidate_data,
                recruiter_data_for_email,
                job_data
            )

        # Update match score in DB
        job.match_score = match["match_score"]

        result_item = {
            "job": job_data,
            "job_id": job.id,
            "analysis": analysis,
            "match": match,
            "resume": resume,
            "outreach": outreach_data,
        }

        # Only process sufficiently matched jobs
        if match["match_score"] < 70:
            skipped_applications += 1
            results.append(result_item)
            continue

        # Check duplicate application
        existing_application = db.query(Application).filter(
            Application.candidate_id == candidate.id,
            Application.job_id == job.id
        ).first()

        if existing_application:
            skipped_applications += 1

        else:
            try:
                # Real browser automation against our demo portal
                submission_url = apply_to_mock_portal(
                    job.id,
                    candidate_data
                )

                application = Application(
                    candidate_id=candidate.id,
                    job_id=job.id,
                    status="applied",
                    applied_date=datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    notes=(
                        "Automatically submitted by autonomous agent. "
                        f"Submission URL: {submission_url}"
                    )
                )

                db.add(application)

                saved_applications += 1
                submitted_applications += 1

                result_item["application_status"] = "applied"
                result_item["submission_url"] = submission_url

            except Exception as e:
                errors.append({
                    "job_id": job.id,
                    "job_title": job.title,
                    "error": str(e)
                })

                result_item["application_status"] = "failed"

        # Save recruiter outreach
        if recruiter and outreach_data:

            existing_outreach = db.query(Outreach).filter(
                Outreach.candidate_id == candidate.id,
                Outreach.recruiter_id == recruiter.id,
                Outreach.job_id == job.id
            ).first()

            if not existing_outreach:

                outreach = Outreach(
                    candidate_id=candidate.id,
                    recruiter_id=recruiter.id,
                    job_id=job.id,
                    subject=outreach_data["subject"],
                    body=outreach_data["body"],
                    status="draft"
                )

                db.add(outreach)
                saved_outreach += 1

        results.append(result_item)

    db.commit()

    return {
        "message": "Autonomous agent completed",
        "candidate": candidate.full_name,
        "jobs_processed": len(db_jobs),
        "applications_saved": saved_applications,
        "applications_submitted": submitted_applications,
        "applications_skipped": skipped_applications,
        "outreach_saved": saved_outreach,
        "errors": errors,
        "results": results
    }
    
@app.post("/agent/apply-matched/{job_id}")
def agent_apply_matched_job(
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

    # Prevent duplicate application
    existing_application = db.query(Application).filter(
        Application.candidate_id == candidate_id,
        Application.job_id == job_id
    ).first()

    if existing_application:
        return {
            "message": "Application already exists",
            "application_id": existing_application.id,
            "status": existing_application.status
        }

    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "experience_years": candidate.experience_years,
        "skills": candidate.skills,
    }

    try:
        submission_url = apply_to_mock_portal(
            job_id,
            candidate_data
        )
    except Exception as e:
        return {
            "error": "Application automation failed",
            "details": str(e)
        }

    application = Application(
        candidate_id=candidate_id,
        job_id=job_id,
        status="applied",
        applied_date=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        notes=f"Submitted through mock portal: {submission_url}"
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Agent application completed",
        "application_id": application.id,
        "candidate_id": candidate_id,
        "job_id": job_id,
        "status": application.status,
        "submission_url": submission_url
    }