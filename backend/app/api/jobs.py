from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.database import get_db
from app.db import models, schemas
from app.services.ranking_engine import rank_candidate
from app.services.explanation_engine import generate_explanation
from app.services.email_service import send_decision_emails
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Job])
def get_jobs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get jobs based on role."""
    if current_user.role == "employer":
        return db.query(models.Job).filter(models.Job.employer_id == current_user.id).all()
    else:
        # Employees see all jobs
        return db.query(models.Job).all()

@router.post("/", response_model=schemas.Job)
def create_job(
    job_data: schemas.JobCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new job."""
    if current_user.role != "employer":
        raise HTTPException(status_code=403, detail="Only employers can create jobs")
    
    emp_id = current_user.id

    req_json = {
        "title": job_data.title,
        "location": job_data.location,
        "years_of_experience": job_data.years_of_experience,
        "qualification": job_data.qualification,
        "required_skills": job_data.required_skills,
        "preferred_skills": job_data.preferred_skills,
        "responsibilities": job_data.responsibilities,
        "raw_text": job_data.description
    }

    job = models.Job(
        employer_id=emp_id,
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        requirements_json=json.dumps(req_json),
        shortlist_size=job_data.shortlist_size
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/{job_id}", response_model=schemas.Job)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job."""
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/rank", response_model=schemas.RankResponse)
def rank_candidates_for_job(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Triggers AI shortlisting for all candidates applied to a job."""
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.employer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to rank this job")
        
    jd_data = json.loads(job.requirements_json) if job.requirements_json else {}
    
    applications = db.query(models.Application).filter(models.Application.job_id == job_id).all()
    
    # 1. Rank all candidates
    rankings = []
    for app in applications:
        resume_data = json.loads(app.candidate.structured_resume_json) if app.candidate.structured_resume_json else {}
        
        scores = rank_candidate(jd_data, resume_data)
        
        app.semantic_score = scores["semantic_score"]
        app.keyword_score = scores["keyword_score"]
        app.required_skill_score = scores["required_skill_score"]
        app.coherence_score = scores["coherence_score"]
        app.final_score = scores["final_score"]
        
        # Save skill matches
        db.query(models.SkillMatch).filter(models.SkillMatch.application_id == app.id).delete()
        for sm in scores["skill_matches"]:
            db_sm = models.SkillMatch(
                application_id=app.id,
                skill=sm.skill,
                required=sm.required,
                matched=sm.matched,
                match_type=sm.match_type,
                evidence=sm.evidence
            )
            db.add(db_sm)
            
        db.commit()
        
        rankings.append({
            "app": app,
            "final_score": app.final_score,
            "scores_dict": scores
        })
        
    # 2. Sort by final score descending
    rankings.sort(key=lambda x: x["final_score"], reverse=True)
    
    # 3. Assign ranks and generate explanations for top candidates
    for idx, item in enumerate(rankings):
        app = item["app"]
        app.rank = idx + 1
        
        # Generate explanation for top 3
        if app.rank <= 3:
            app.explanation = generate_explanation(app.candidate.name, item["scores_dict"])
        else:
            app.explanation = None
            
        if app.rank <= job.shortlist_size:
            app.status = "shortlisted"
        else:
            app.status = "rejected"
            
        db.commit()
        
    db.refresh(job)
    
    # 4. Trigger automated emails
    decisions = []
    for app in job.applications:
        decisions.append({
            "name": app.candidate.name,
            "email": app.candidate.email,
            "status": app.status
        })
    send_decision_emails(job.title, job.company, decisions)
    
    return {"applications": sorted(job.applications, key=lambda x: x.rank if x.rank else 999)}
