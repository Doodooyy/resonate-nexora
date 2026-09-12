import json
from typing import Dict, Any, List
from app.services.keyword_matcher import check_explicit_match, find_skill_evidence
from app.services.semantic_matcher import calculate_semantic_score
from app.core.config import get_settings
from app.db.schemas import SkillMatch

settings = get_settings()

def compute_coherence_score(resume_sections: Dict[str, str], skill_matches: List[SkillMatch]) -> float:
    """
    Computes a coherence/evidence score.
    Higher score if skill appears in experience/projects, lower if only in skills list.
    """
    if not skill_matches:
        return 0.0
        
    total_evidence_score = 0
    matched_skills_count = 0
    
    for match in skill_matches:
        if not match.matched:
            continue
            
        matched_skills_count += 1
        skill = match.skill
        
        # Check where it appears
        has_in_exp = check_explicit_match(resume_sections.get("experience", ""), skill)[0]
        has_in_proj = check_explicit_match(resume_sections.get("projects", ""), skill)[0]
        has_in_skills = check_explicit_match(resume_sections.get("skills", ""), skill)[0]
        
        # Strong evidence (experience or project) = 1.0
        # Weak evidence (skills list only) = 0.5
        if has_in_exp or has_in_proj:
            total_evidence_score += 1.0
        elif has_in_skills:
            total_evidence_score += 0.5
        else:
            # Found somewhere else (e.g., summary)
            total_evidence_score += 0.7
            
    if matched_skills_count == 0:
        return 0.0
        
    # Average evidence score scaled to 100
    return (total_evidence_score / matched_skills_count) * 100

def rank_candidate(jd_data: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core ranking engine. Combines semantic, keyword, required skills, and coherence.
    Returns scores scaled 0-100.
    """
    raw_resume_text = resume_data.get("raw_text", "")
    resume_sections = resume_data.get("sections", {})
    jd_raw_text = jd_data.get("raw_text", "")
    
    # 1. Keyword Matching
    required_skills = jd_data.get("required_skills", [])
    preferred_skills = jd_data.get("preferred_skills", [])
    
    skill_match_results = []
    
    matched_required_count = 0
    
    for skill in required_skills:
        matched, match_type = check_explicit_match(raw_resume_text, skill)
        evidence = find_skill_evidence(resume_sections, skill) if matched else ""
        skill_match_results.append(SkillMatch(
            skill=skill,
            required=True,
            matched=matched,
            match_type=match_type,
            evidence=evidence
        ))
        if matched:
            matched_required_count += 1
            
    for skill in preferred_skills:
        matched, match_type = check_explicit_match(raw_resume_text, skill)
        evidence = find_skill_evidence(resume_sections, skill) if matched else ""
        skill_match_results.append(SkillMatch(
            skill=skill,
            required=False,
            matched=matched,
            match_type=match_type,
            evidence=evidence
        ))
        
    # Keyword score (simple % of all skills matched)
    total_skills = len(required_skills) + len(preferred_skills)
    matched_total = sum(1 for sm in skill_match_results if sm.matched)
    keyword_score = (matched_total / total_skills * 100) if total_skills > 0 else 100.0
    
    # 2. Required Skill Coverage Score (gating)
    required_score = (matched_required_count / len(required_skills) * 100) if required_skills else 100.0
    
    # 3. Semantic Score
    semantic_raw = calculate_semantic_score(jd_raw_text, resume_sections)
    semantic_score = semantic_raw * 100
    
    # 4. Coherence/Evidence Score
    coherence_score = compute_coherence_score(resume_sections, skill_match_results)
    
    # --- Final Score Calculation ---
    w_sem = settings.WEIGHT_SEMANTIC
    w_key = settings.WEIGHT_KEYWORD
    w_req = settings.WEIGHT_REQUIRED
    w_coh = settings.WEIGHT_COHERENCE
    
    base_score = (
        (semantic_score * w_sem) + 
        (keyword_score * w_key) + 
        (required_score * w_req) + 
        (coherence_score * w_coh)
    )
    
    # Penalty for missing required skills and mandatory criteria
    penalty_multiplier = 1.0
    
    # Required skills penalty
    if required_skills:
        missing_fraction = 1.0 - (required_score / 100.0)
        penalty_multiplier = max(0.40, penalty_multiplier - (missing_fraction * 0.6))
        
    # Mandatory Criteria Penalties
    jd_location = jd_data.get("location", "")
    jd_qual = jd_data.get("qualification", "")
    jd_yoe = jd_data.get("years_of_experience", 0)
    
    extracted_yoe = resume_data.get("extracted_yoe", 0)
    
    # Location match
    if jd_location and jd_location.lower() != "remote":
        if jd_location.lower() not in raw_resume_text.lower():
            penalty_multiplier -= 0.15
            
    # Qualification match
    if jd_qual:
        matched_qual, _ = check_explicit_match(raw_resume_text, jd_qual)
        if not matched_qual:
            penalty_multiplier -= 0.15
            
    # Experience match
    if jd_yoe and extracted_yoe > 0:
        if extracted_yoe < jd_yoe:
            yoe_deficit = (jd_yoe - extracted_yoe) / jd_yoe
            penalty_multiplier -= (yoe_deficit * 0.20) # Up to 20% penalty
            
    # Bound penalty between 0.20 and 1.0
    penalty_multiplier = max(0.20, min(1.0, penalty_multiplier))
        
    final_score = base_score * penalty_multiplier
    
    return {
        "semantic_score": round(semantic_score, 1),
        "keyword_score": round(keyword_score, 1),
        "required_skill_score": round(required_score, 1),
        "coherence_score": round(coherence_score, 1),
        "final_score": round(final_score, 1),
        "skill_matches": skill_match_results
    }
