from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os
import json

from app.db.database import get_db
from app.db import models, schemas
from app.services.pdf_parser import parse_pdf
from app.services.resume_parser import structure_resume

router = APIRouter()

UPLOAD_DIR = "data/resumes"

@router.post("/jobs/{job_id}/apply")
async def apply_to_job(
    job_id: int, 
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Employee workflow: Upload a resume to apply for a job."""
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, resume.filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
        
    # Parse PDF
    raw_text = parse_pdf(file_path)
    structured_data = structure_resume(raw_text)
    
    # Create or update candidate
    email = structured_data.get("email") or f"unknown_{resume.filename}@example.com"
    candidate = db.query(models.Candidate).filter(models.Candidate.email == email).first()
    
    if not candidate:
        candidate = models.Candidate(
            name=structured_data.get("name", "Unknown Candidate"),
            email=email,
            resume_filename=resume.filename,
            resume_text=raw_text,
            structured_resume_json=json.dumps(structured_data)
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    
    # Create application
    application = db.query(models.Application).filter(
        models.Application.job_id == job_id,
        models.Application.candidate_id == candidate.id
    ).first()
    
    if not application:
        application = models.Application(
            job_id=job_id,
            candidate_id=candidate.id
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        
    return {"message": "Application submitted successfully", "application_id": application.id}
