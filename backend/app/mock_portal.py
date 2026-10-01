from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/mock-portal/{job_id}", response_class=HTMLResponse)
def mock_application_portal(job_id: int):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo Job Application</title>
    </head>

    <body style="font-family: Arial; max-width: 700px; margin: 40px auto;">

        <h1>Demo Job Application</h1>
        <p>Job ID: {job_id}</p>

        <form method="post" action="/mock-portal/{job_id}/submit">

            <label>Full Name</label><br>
            <input name="full_name" required><br><br>

            <label>Email</label><br>
            <input name="email" type="email" required><br><br>

            <label>Phone</label><br>
            <input name="phone"><br><br>

            <label>Experience (Years)</label><br>
            <input name="experience_years" type="number" min="0"><br><br>

            <label>Skills</label><br>
            <textarea name="skills"></textarea><br><br>

            <button type="submit">
                Submit Application
            </button>

        </form>

    </body>
    </html>
    """


@router.post("/mock-portal/{job_id}/submit", response_class=HTMLResponse)
def submit_application(
    job_id: int,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    experience_years: int = Form(0),
    skills: str = Form(""),
):
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial; max-width: 700px; margin: 40px auto;">

        <h1>Application Submitted</h1>

        <p><strong>Job ID:</strong> {job_id}</p>
        <p><strong>Name:</strong> {full_name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Experience:</strong> {experience_years} years</p>
        <p><strong>Skills:</strong> {skills}</p>

        <p>Demo application submitted successfully.</p>

    </body>
    </html>
    """