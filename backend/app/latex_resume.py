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


import os
import subprocess
import tempfile


def compile_latex_to_pdf(latex_content):
    pdf_latex_path = os.getenv(
        "PDFLATEX_PATH",
        "pdflatex"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = os.path.join(
            temp_dir,
            "resume.tex"
        )

        with open(
            tex_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(latex_content)

        result = subprocess.run(
            [
                pdf_latex_path,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "resume.tex"
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stdout + "\n" + result.stderr
            )

        pdf_path = os.path.join(
            temp_dir,
            "resume.pdf"
        )

        with open(pdf_path, "rb") as file:
            return file.read()