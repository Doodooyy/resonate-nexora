import os
import sys
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from datetime import datetime

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal, engine, Base
from app.db import models
from app.services.pdf_parser import parse_pdf
from app.services.resume_parser import structure_resume

# Demo Job Description
DEMO_JD = """
Full Stack Developer
Company: TechCorp

We are looking for an experienced Full Stack Developer to join our team. 
The ideal candidate will have strong experience in building scalable web applications.

Required Skills:
- React
- Node.js
- REST APIs
- MongoDB

Preferred Skills:
- AWS
- Docker
- GraphQL

Responsibilities:
- Build and maintain RESTful backend services
- Develop responsive frontend components
- Must be a rockstar ninja willing to work in a fast-paced environment. (Note: Should flag as bias)
- Must be a graduate from a top-tier university.
"""

DUMMY_CANDIDATES = [
    {
        "name": "Rahul Sharma",
        "email": "rahul.s@example.com",
        "text": [
            "Rahul Sharma",
            "rahul.s@example.com",
            "",
            "SUMMARY",
            "Full Stack Developer with 4 years of experience building web applications.",
            "",
            "SKILLS",
            "React, Node.js, Express, MongoDB, REST APIs, HTML, CSS",
            "",
            "EXPERIENCE",
            "Software Engineer - Startup Inc (2020 - Present)",
            "Built a highly scalable e-commerce frontend using React and Redux.",
            "Developed REST APIs with Node.js and Express to serve over 10k users.",
            "",
            "PROJECTS",
            "Inventory Dashboard: Built an inventory management system using React, Node.js, and MongoDB.",
            "https://github.com/rahulsharma/inventory-dashboard"
        ]
    },
    {
        "name": "Ananya Rao",
        "email": "ananya.r@example.com",
        "text": [
            "Ananya Rao",
            "ananya.r@example.com",
            "",
            "PROFILE",
            "Frontend focused software engineer with some backend experience.",
            "",
            "TECHNICAL SKILLS",
            "React.js, JavaScript, Python, Django, SQL",
            "",
            "WORK EXPERIENCE",
            "Frontend Developer - WebSolutions (2021 - 2023)",
            "Created responsive UI components using React.js and Tailwind.",
            "Integrated frontend with Python Django backend.",
            "",
            "PROJECTS",
            "Weather App: Built a simple weather app using React and public APIs."
        ]
    },
    {
        "name": "Alex Johnson",
        "email": "alex.j@example.com",
        "text": [
            "Alex Johnson",
            "alex.j@example.com",
            "",
            "ABOUT ME",
            "Backend engineer specializing in scalable systems.",
            "",
            "CORE COMPETENCIES",
            "Node.js, Express, RESTful APIs, PostgreSQL, AWS, Docker",
            "",
            "PROFESSIONAL EXPERIENCE",
            "Backend Engineer - CloudCorp (2019 - Present)",
            "Architected REST APIs in Node.js and deployed them using Docker on AWS.",
            "Optimized PostgreSQL queries.",
            "",
            "CERTIFICATIONS",
            "AWS Certified Developer"
        ]
    },
]

def generate_pdf(filename: str, lines: list):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    for line in lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()

def seed_db():
    print("Recreating database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Create Employer User
        employer = models.User(email="employer@example.com", password_hash="hashed_pw", role="employer")
        db.add(employer)
        db.commit()
        db.refresh(employer)
        
        # 2. Create Job
        job = models.Job(
            employer_id=employer.id,
            title="Full Stack Developer",
            company="TechCorp",
            description=DEMO_JD,
            requirements_json=json.dumps({
                "title": "Full Stack Developer",
                "required_skills": ["React", "Node.js", "REST APIs", "MongoDB"],
                "preferred_skills": ["AWS", "Docker", "GraphQL"],
                "raw_text": DEMO_JD
            }),
            shortlist_size=3
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        print(f"Created Job: {job.title}")
        
        # 3. Create Candidates and Applications
        resumes_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'resumes')
        
        for cand_data in DUMMY_CANDIDATES:
            filename = cand_data["name"].replace(" ", "_").lower() + ".pdf"
            pdf_path = os.path.join(resumes_dir, filename)
            
            print(f"Generating PDF for {cand_data['name']}...")
            generate_pdf(pdf_path, cand_data["text"])
            
            # Parse it
            raw_text = parse_pdf(pdf_path)
            structured_data = structure_resume(raw_text)
            
            candidate = models.Candidate(
                name=cand_data["name"],
                email=cand_data["email"],
                resume_filename=filename,
                resume_text=raw_text,
                structured_resume_json=json.dumps(structured_data)
            )
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
            
            application = models.Application(
                job_id=job.id,
                candidate_id=candidate.id
            )
            db.add(application)
            
        db.commit()
        print("Database seeded successfully with demo data.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
