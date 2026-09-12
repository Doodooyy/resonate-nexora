from google import genai
from google.genai import types
from app.core.config import get_settings
from typing import Dict, Any

settings = get_settings()

def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        return None
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_explanation(candidate_name: str, rank_data: Dict[str, Any]) -> str:
    """
    Generates a natural-language explanation for why a candidate ranked where they did,
    based strictly on the provided structured evidence.
    """
    client = get_gemini_client()
    
    # Format the evidence
    matched_req = [m for m in rank_data["skill_matches"] if m.required and m.matched]
    missing_req = [m for m in rank_data["skill_matches"] if m.required and not m.matched]
    matched_pref = [m for m in rank_data["skill_matches"] if not m.required and m.matched]
    
    evidence_lines = []
    for m in rank_data["skill_matches"]:
        if m.matched and m.evidence:
            evidence_lines.append(f"- {m.skill}: {m.evidence}")
            
    prompt = f"""
You are an expert technical recruiter explaining why a candidate ranked highly in an AI shortlisting system.
Candidate Name: {candidate_name}

Scores:
- Semantic Match: {rank_data['semantic_score']}/100
- Keyword Match: {rank_data['keyword_score']}/100
- Required Skill Coverage: {rank_data['required_skill_score']}/100
- Evidence Coherence: {rank_data['coherence_score']}/100
- Final Score: {rank_data['final_score']}/100

Matched Required Skills: {', '.join([m.skill for m in matched_req]) if matched_req else 'None'}
Missing Required Skills: {', '.join([m.skill for m in missing_req]) if missing_req else 'None'}
Matched Preferred Skills: {', '.join([m.skill for m in matched_pref]) if matched_pref else 'None'}

Evidence found in resume:
{chr(10).join(evidence_lines) if evidence_lines else 'No explicit evidence snippets extracted.'}

INSTRUCTIONS:
Write a concise (3-4 sentences), professional summary of WHY this candidate is a strong fit.
Do NOT invent facts. Rely ONLY on the scores and evidence provided above.
If they are missing required skills, mention it constructively.
Keep it strictly evidence-based and explainable.
"""
    
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            return response.text
        except Exception as e:
            print(f"LLM Error: {e}")
            # Fall through to template fallback
            pass
            
    # Template Fallback if no LLM or error
    explanation = f"{candidate_name} achieved a final score of {rank_data['final_score']} out of 100. "
    explanation += f"Their semantic alignment with the JD is {rank_data['semantic_score']}/100, and they covered {rank_data['required_skill_score']}% of required skills. "
    
    if matched_req:
        explanation += f"They demonstrated required skills such as {', '.join([m.skill for m in matched_req])}. "
    if missing_req:
        explanation += f"However, they appear to be missing {', '.join([m.skill for m in missing_req])}. "
        
    explanation += f"Their evidence coherence score is {rank_data['coherence_score']}/100."
    return explanation

def compare_candidates(cand_a_name: str, cand_a_data: Dict[str, Any], cand_b_name: str, cand_b_data: Dict[str, Any]) -> str:
    """Answers why Candidate A ranked above Candidate B."""
    client = get_gemini_client()
    
    prompt = f"""
You are an expert technical recruiter explaining why {cand_a_name} ranked above {cand_b_name} in an AI shortlisting system.
Do NOT invent facts. Rely ONLY on the scores provided.

Candidate A ({cand_a_name}):
- Final Score: {cand_a_data['final_score']}/100
- Semantic Match: {cand_a_data['semantic_score']}/100
- Required Coverage: {cand_a_data['required_skill_score']}/100
- Coherence: {cand_a_data['coherence_score']}/100

Candidate B ({cand_b_name}):
- Final Score: {cand_b_data['final_score']}/100
- Semantic Match: {cand_b_data['semantic_score']}/100
- Required Coverage: {cand_b_data['required_skill_score']}/100
- Coherence: {cand_b_data['coherence_score']}/100

Explain concisely why Candidate A is the stronger fit based strictly on the differences in these scores.
"""
    
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            return response.text
        except Exception as e:
            pass
            
    return f"{cand_a_name} ranked higher primarily due to a final score of {cand_a_data['final_score']} compared to {cand_b_data['final_score']} for {cand_b_name}."
