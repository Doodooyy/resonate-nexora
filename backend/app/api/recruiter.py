from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models, schemas
from app.services.explanation_engine import compare_candidates
import json

router = APIRouter()

@router.post("/jobs/{job_id}/compare")
def compare_candidates_api(
    job_id: int, 
    cand_a_id: int, 
    cand_b_id: int,
    db: Session = Depends(get_db)
):
    """Answers why Candidate A ranked above Candidate B."""
    app_a = db.query(models.Application).filter(
        models.Application.job_id == job_id,
        models.Application.candidate_id == cand_a_id
    ).first()
    
    app_b = db.query(models.Application).filter(
        models.Application.job_id == job_id,
        models.Application.candidate_id == cand_b_id
    ).first()
    
    if not app_a or not app_b:
        raise HTTPException(status_code=404, detail="One or both candidates not found for this job")
        
    cand_a_data = {
        "final_score": app_a.final_score,
        "semantic_score": app_a.semantic_score,
        "required_skill_score": app_a.required_skill_score,
        "coherence_score": app_a.coherence_score
    }
    
    cand_b_data = {
        "final_score": app_b.final_score,
        "semantic_score": app_b.semantic_score,
        "required_skill_score": app_b.required_skill_score,
        "coherence_score": app_b.coherence_score
    }
    
    explanation = compare_candidates(app_a.candidate.name, cand_a_data, app_b.candidate.name, cand_b_data)
    
    return {"explanation": explanation}
