from typing import List, Dict, Any
from app.db.schemas import Job

# Extremely simple heuristic-based bias detector as fallback
# A robust one would use an LLM
BIAS_HEURISTICS = [
    {
        "pattern": "top-tier university",
        "category": "Education Bias",
        "severity": "Medium",
        "explanation": "Implies prestige is required over actual skills.",
        "suggestion": "Degree in Computer Science or equivalent practical experience"
    },
    {
        "pattern": "native speaker",
        "category": "Nationality/Language Bias",
        "severity": "High",
        "explanation": "Can be discriminatory. Fluency is usually what is required.",
        "suggestion": "Fluent in English"
    },
    {
        "pattern": "young and energetic",
        "category": "Age Bias",
        "severity": "High",
        "explanation": "Age-coded language that excludes older candidates.",
        "suggestion": "Dynamic and proactive"
    },
    {
        "pattern": "ninja",
        "category": "Gender/Culture Bias",
        "severity": "Low",
        "explanation": "Tech culture jargon that can alienate some candidates.",
        "suggestion": "Expert or Specialist"
    },
    {
        "pattern": "rockstar",
        "category": "Gender/Culture Bias",
        "severity": "Low",
        "explanation": "Tech culture jargon that can alienate some candidates.",
        "suggestion": "Expert or Specialist"
    }
]

def analyze_jd_for_bias(jd_text: str) -> List[Dict[str, Any]]:
    """
    Scans a JD for potentially exclusionary phrasing.
    """
    flags = []
    text_lower = jd_text.lower()
    
    for rule in BIAS_HEURISTICS:
        if rule["pattern"] in text_lower:
            flags.append({
                "category": rule["category"],
                "severity": rule["severity"],
                "phrase": rule["pattern"],
                "explanation": rule["explanation"],
                "suggestion": rule["suggestion"]
            })
            
    return flags
