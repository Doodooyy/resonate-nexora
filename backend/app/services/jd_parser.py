import re
import json
from typing import Dict, Any, List

def parse_jd(raw_text: str) -> Dict[str, Any]:
    """
    Parses a Job Description into structured data.
    Without an LLM, uses simple keyword heuristics.
    """
    lines = raw_text.split('\n')
    
    title = lines[0] if lines else "Unknown Job"
    
    required_skills = []
    preferred_skills = []
    
    current_section = "description"
    
    for line in lines[1:]:
        l_lower = line.lower()
        if "requirement" in l_lower or "required" in l_lower or "must have" in l_lower:
            current_section = "required"
            continue
        elif "preferred" in l_lower or "nice to have" in l_lower or "bonus" in l_lower:
            current_section = "preferred"
            continue
        elif "responsibility" in l_lower or "what you will do" in l_lower:
            current_section = "responsibilities"
            continue
            
        # Very simple extraction if bullet point
        if line.strip().startswith("-") or line.strip().startswith("•") or line.strip().startswith("*"):
            item = re.sub(r'^[-•*]\s*', '', line.strip())
            if current_section == "required":
                # Basic heuristic: if it's short, it might be a specific skill
                if len(item) < 30:
                    required_skills.append(item)
                else:
                    # Look for known skills inside the sentence - would need NLP here
                    # For now, just add the whole bullet, the matcher will have to handle phrase matches
                    required_skills.append(item)
            elif current_section == "preferred":
                if len(item) < 30:
                    preferred_skills.append(item)
                else:
                    preferred_skills.append(item)
                    
    return {
        "title": title.strip(),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "raw_text": raw_text
    }
