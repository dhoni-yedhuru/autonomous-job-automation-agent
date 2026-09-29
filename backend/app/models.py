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