import re
import json
from typing import Dict, Any, List

# Common section headers in resumes
SECTION_MAPPING = {
    "summary": ["summary", "profile", "objective", "about me"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "employment"],
    "education": ["education", "academic background", "academic qualifications"],
    "skills": ["skills", "technical skills", "technologies", "core competencies", "tech stack"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "licenses"],
    "achievements": ["achievements", "awards", "honors"]
}

def normalize_header(line: str) -> str:
    """Normalizes a header line to a canonical section name if it matches."""
    cleaned = line.strip().lower()
    # Remove non-alphanumeric chars for matching
    cleaned = re.sub(r'[^a-z0-9\s]', '', cleaned).strip()
    
    for section, aliases in SECTION_MAPPING.items():
        if cleaned in aliases:
            return section
    return ""

def parse_resume_sections(text: str) -> Dict[str, str]:
    """Splits resume text into canonical sections."""
    lines = text.split('\n')
    sections = {key: [] for key in SECTION_MAPPING.keys()}
    sections["unknown"] = []
    
    current_section = "unknown"
    
    for line in lines:
        if not line.strip():
            continue
            
        # Check if line is a header (usually short, uppercase or Title Case)
        # Heuristic: < 50 chars, doesn't contain a lot of lowercase words, matches mapping
        if len(line.strip()) < 50:
            header = normalize_header(line)
            if header:
                current_section = header
                continue
                
        # Heuristic: Check if line is ALL CAPS and short, might be a header we missed
        if line.strip().isupper() and len(line.strip()) < 30 and current_section == "unknown":
             header = normalize_header(line)
             if header:
                 current_section = header
                 continue
                 
        sections[current_section].append(line)
        
    # Join lists into strings
    return {k: "\n".join(v) for k, v in sections.items() if v}

def extract_entities(text: str) -> Dict[str, Any]:
    """Extracts basic entities like emails and links from text."""
    # Simple email regex
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    email = email_match.group(0) if email_match else ""
    
    # Github regex
    github_urls = re.findall(r'(https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+)', text)
    
    # Years of Experience regex (e.g. 5 years, 10+ yrs)
    yoe_matches = re.findall(r'(\d+)\+?\s*(?:years|yrs)\b', text.lower())
    yoe = 0
    if yoe_matches:
        yoe = max([int(m) for m in yoe_matches if m.isdigit()])
    
    return {
        "email": email,
        "github_urls": github_urls,
        "extracted_yoe": yoe
    }

def structure_resume(raw_text: str) -> Dict[str, Any]:
    """Creates a structured JSON representation of the resume."""
    sections = parse_resume_sections(raw_text)
    entities = extract_entities(raw_text)
    
    # Extract name (basic heuristic: first non-empty line)
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    name = lines[0] if lines else "Unknown"
    
    return {
        "name": name,
        "email": entities["email"],
        "github_urls": entities["github_urls"],
        "extracted_yoe": entities.get("extracted_yoe", 0),
        "sections": sections,
        "raw_text": raw_text
    }
