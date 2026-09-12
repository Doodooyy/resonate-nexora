import pytest
from app.services.ranking_engine import rank_candidate
from app.services.keyword_matcher import normalize_skill

def test_skill_normalization():
    assert normalize_skill("NodeJS") == "node.js"
    assert normalize_skill("react.js") == "react"
    assert normalize_skill("restful api") == "rest apis"
    assert normalize_skill("UnknownSkill") == "unknownskill"

def test_ranking_logic_strong_match():
    jd = {
        "required_skills": ["React", "Node.js"],
        "preferred_skills": ["Docker"],
        "raw_text": "We need a frontend engineer with React and Node.js. Docker is a plus."
    }
    
    resume = {
        "raw_text": "I am a frontend developer. I have 4 years of experience with React and Node.js. I used Docker.",
        "sections": {
            "skills": "React, Node.js, Docker",
            "experience": "Worked heavily with React and Node.js."
        }
    }
    
    scores = rank_candidate(jd, resume)
    
    assert scores["keyword_score"] == 100.0
    assert scores["required_skill_score"] == 100.0
    assert scores["coherence_score"] > 80.0
    assert scores["final_score"] > 70.0
    
def test_ranking_logic_missing_required():
    jd = {
        "required_skills": ["React", "Node.js"],
        "preferred_skills": [],
        "raw_text": "Looking for React and Node.js"
    }
    
    resume = {
        "raw_text": "I am a developer. I use Python and Django.",
        "sections": {
            "skills": "Python, Django"
        }
    }
    
    scores = rank_candidate(jd, resume)
    
    assert scores["keyword_score"] == 0.0
    assert scores["required_skill_score"] == 0.0
    # The penalty should severely reduce the final score
    assert scores["final_score"] < 40.0
