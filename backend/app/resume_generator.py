def generate_resume_content(candidate, job):
    return {
        "candidate_name": candidate.get("full_name"),
        "email": candidate.get("email"),
        "phone": candidate.get("phone"),
        "location": candidate.get("location"),
        "target_title": job.get("title"),
        "skills": candidate.get("skills"),
        "master_resume": candidate.get("master_resume"),
        "job_company": job.get("company"),
        "job_required_skills": job.get("required_skills"),
    }