from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.services.bias_detector import analyze_jd_for_bias

router = APIRouter()

@router.get("/jobs/{job_id}/bias")
def detect_bias(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    flags = analyze_jd_for_bias(job.description)
    
    return {"flags": flags}
