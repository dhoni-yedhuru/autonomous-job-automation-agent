from datetime import datetime

from job_discovery import search_jobs
from job_analysis import analyze_job
from matching import analyze_match
from resume_generator import generate_resume_content
from outreach import generate_outreach_email


def run_agent(candidate: dict, recruiter: dict | None = None):
    """
    Main autonomous career-agent pipeline.

    Discover → Analyze → Match → Prepare Resume
    → Prepare Outreach
    """

    discovered_jobs = search_jobs()
    results = []

    candidate_skills = candidate.get("skills", "")

    for job in discovered_jobs:
        analysis = analyze_job(job)

        required_skills = job.get("required_skills", "")

        match = analyze_match(
            candidate_skills,
            required_skills
        )

        resume = generate_resume_content(
            candidate,
            job
        )

        outreach = None

        if recruiter:
            outreach = generate_outreach_email(
                candidate,
                recruiter,
                job
            )

        results.append({
            "job": job,
            "analysis": analysis,
            "match": match,
            "resume": resume,
            "outreach": outreach,
            "processed_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

    return {
        "candidate": candidate.get("full_name"),
        "jobs_discovered": len(discovered_jobs),
        "results": results
    }