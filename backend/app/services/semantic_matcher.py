from sentence_transformers import SentenceTransformer, util
import torch

# Load a lightweight, performant model for semantic matching
# all-MiniLM-L6-v2 is fast and good for generic sentence similarity
# multi-qa-mpnet-base-cos-v1 is better for QA/retrieval but larger.
MODEL_NAME = 'all-MiniLM-L6-v2'
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculates cosine similarity between two texts."""
    if not text1.strip() or not text2.strip():
        return 0.0
        
    model = get_model()
    
    # Compute embeddings
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_score = util.cos_sim(embedding1, embedding2).item()
    
    # Ensure it's between 0 and 1
    return max(0.0, min(1.0, cosine_score))

def calculate_semantic_score(jd_text: str, resume_sections: dict) -> float:
    """
    Computes a weighted semantic score using different sections of the resume.
    """
    model = get_model()
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    
    def get_sim(section_text: str) -> float:
        if not section_text.strip():
            return 0.0
        sec_embedding = model.encode(section_text, convert_to_tensor=True)
        return max(0.0, min(1.0, util.cos_sim(jd_embedding, sec_embedding).item()))
        
    # Weights for different sections based on product vision
    # 0.40 * experience_similarity + 0.30 * project_similarity + 0.20 * skills_similarity + 0.10 * summary_similarity
    
    exp_sim = get_sim(resume_sections.get("experience", ""))
    proj_sim = get_sim(resume_sections.get("projects", ""))
    skills_sim = get_sim(resume_sections.get("skills", ""))
    summary_sim = get_sim(resume_sections.get("summary", ""))
    
    # If a section is missing, we shouldn't necessarily penalize the whole semantic score if other sections are strong,
    # but for simplicity we stick to the weighted sum as requested.
    score = (0.40 * exp_sim) + (0.30 * proj_sim) + (0.20 * skills_sim) + (0.10 * summary_sim)
    
    # If the resume is completely unsectioned, fallback to full text similarity
    if score == 0 and resume_sections.get("unknown"):
         return get_sim(resume_sections.get("unknown", ""))
         
    return score
