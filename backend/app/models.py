from sqlalchemy import Column, Integer, String, Text
from database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(30))
    location = Column(String(100))
    experience_years = Column(Integer, default=0)
    target_titles = Column(Text)
    skills = Column(Text)
    master_resume = Column(Text)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    job_url = Column(String(500))
    source = Column(String(100))
    description = Column(Text)
    required_skills = Column(Text)
    salary = Column(String(100))
    work_mode = Column(String(50))
    posted_date = Column(String(50))
    status = Column(String(50), default="new")
    match_score = Column(Integer, default=0)
    
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, nullable=False)
    job_id = Column(Integer, nullable=False)
    status = Column(String(50), default="saved")
    applied_date = Column(String(50))
    notes = Column(Text)