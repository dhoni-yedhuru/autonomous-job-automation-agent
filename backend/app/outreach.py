def generate_outreach_email(
    candidate: dict,
    recruiter: dict,
    job: dict
):
    candidate_name = candidate.get("full_name", "Candidate")
    recruiter_name = recruiter.get("name", "Recruiter")
    company = job.get("company") or recruiter.get("company", "")
    job_title = job.get("title", "the role")
    skills = candidate.get("skills", "")

    subject = f"Application for {job_title} – {candidate_name}"

    body = f"""Hi {recruiter_name},

I hope you're doing well.

I'm {candidate_name}, and I'm interested in the {job_title} opportunity at {company}.

My experience includes working with {skills}. I believe my background could be relevant to this role.

I'd be happy to share my resume and discuss the opportunity further.

Thank you for your time.

Best regards,
{candidate_name}
{candidate.get("email", "")}
{candidate.get("phone", "")}
"""

    return {
        "subject": subject,
        "body": body,
        "recruiter": recruiter_name,
        "company": company,
        "job_title": job_title,
    }