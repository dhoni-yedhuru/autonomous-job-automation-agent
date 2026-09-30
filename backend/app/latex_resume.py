def generate_latex_resume(candidate, job):
    name = candidate.get("full_name", "")
    email = candidate.get("email", "")
    phone = candidate.get("phone", "")
    location = candidate.get("location", "")
    skills = candidate.get("skills", "")
    master_resume = candidate.get("master_resume", "")
    target_title = job.get("title", "")
    company = job.get("company", "")

    latex = f"""
\\documentclass{{article}}

\\usepackage[margin=0.7in]{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{enumitem}}

\\begin{{document}}

\\begin{{center}}
    {{\\LARGE \\textbf{{{name}}}}}\\\\
    {email} \\quad | \\quad {phone} \\quad | \\quad {location}
\\end{{center}}

\\section*{{Target Role}}
{target_title} at {company}

\\section*{{Skills}}
{skills}

\\section*{{Resume}}
{master_resume}

\\end{{document}}
"""

    return latex