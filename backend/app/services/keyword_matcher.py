import re
from rapidfuzz import process, fuzz
from typing import List, Dict, Tuple, Optional

# A predefined ontology of canonical skills to aliases
SKILL_ONTOLOGY = {
    "javascript": ["js", "ecmascript", "javascript"],
    "node.js": ["node", "nodejs", "node.js", "node js"],
    "react": ["react", "reactjs", "react.js"],
    "mongodb": ["mongo", "mongodb"],
    "rest apis": ["rest", "rest api", "restful api", "restful services", "rest apis"],
    "python": ["python", "python3"],
    "fastapi": ["fastapi", "fast api"],
    "docker": ["docker", "containerization", "dockerize"],
    "aws": ["aws", "amazon web services"],
    "sql": ["sql", "mysql", "postgresql", "postgres"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "tailwind", "tailwindcss"],
    "git": ["git", "github", "gitlab", "version control"],
}

def normalize_skill(skill: str) -> str:
    """Returns the canonical name for a skill, or the lowercased skill if not in ontology."""
    skill_clean = skill.strip().lower()
    for canonical, aliases in SKILL_ONTOLOGY.items():
        if skill_clean in aliases:
            return canonical
    return skill_clean

def check_explicit_match(resume_text: str, skill: str) -> Tuple[bool, str]:
    """
    Checks if a skill or its aliases appear explicitly in the text.
    Returns (matched, match_type).
    """
    canonical = normalize_skill(skill)
    aliases = SKILL_ONTOLOGY.get(canonical, [canonical])
    
    text_lower = resume_text.lower()
    
    for alias in aliases:
        # Use word boundaries for strict matching
        # special case for some skills with punctuation
        escaped_alias = re.escape(alias)
        pattern = rf"\b{escaped_alias}\b"
        
        if re.search(pattern, text_lower):
            if alias == skill.lower():
                return True, "exact"
            return True, "alias"
            
    # Fuzzy matching fallback if it's not a generic word
    # For example, catching typos like 'rectjs' if they are very close
    # Only if the skill itself is long enough
    if len(skill) > 4:
         # simple token extraction from text to compare
         tokens = set(re.findall(r'\b\w+\b', text_lower))
         for t in tokens:
             if fuzz.ratio(skill.lower(), t) > 90:
                 return True, "fuzzy"
                 
    return False, ""

def find_skill_evidence(sections: Dict[str, str], skill: str) -> str:
    """Finds snippet of evidence where the skill was mentioned."""
    canonical = normalize_skill(skill)
    aliases = SKILL_ONTOLOGY.get(canonical, [canonical])
    
    for section_name, content in sections.items():
        if not content:
            continue
            
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            for alias in aliases:
                pattern = rf"\b{re.escape(alias)}\b"
                if re.search(pattern, line_lower):
                    return f"[{section_name.upper()}] {line.strip()}"
                    
    return ""
