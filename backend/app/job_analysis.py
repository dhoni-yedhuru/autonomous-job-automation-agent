def analyze_job(job):
    description = job.get("description") or ""
    required_skills = job.get("required_skills") or ""

    text = f"{description} {required_skills}".lower()

    skills = [
        "python",
        "fastapi",
        "django",
        "flask",
        "postgresql",
        "mysql",
        "react",
        "javascript",
        "typescript",
        "node.js",
        "java",
        "spring",
        "aws",
        "docker",
        "kubernetes",
        "git",
    ]

    detected_skills = [
        skill
        for skill in skills
        if skill.lower() in text
    ]

    return {
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "work_mode": job.get("work_mode"),
        "required_skills": detected_skills,
        "description": description,
    }