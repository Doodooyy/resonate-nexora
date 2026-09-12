# NEXORA - Explainable AI Resume Shortlisting Engine

NEXORA is a transparent, evidence-based AI shortlisting engine. Unlike traditional "black-box" LLM shortlisting tools, Nexora calculates scores mathematically using semantic similarity, explicit keyword matching, and evidence coherence, and only uses LLMs to translate these calculated scores into natural-language explanations.

## How Nexora Ranks Candidates

The final ranking score is calculated using the following components:

1. **Semantic Matching (40%)**: Calculates the cosine similarity between the Job Description embeddings and the candidate's Resume sections (Experience, Projects, Skills) using the `all-MiniLM-L6-v2` SentenceTransformer model.
2. **Keyword Matching (35%)**: Performs explicit token matching with alias resolution (e.g. `NodeJS` -> `node.js`) and fuzzy matching using RapidFuzz.
3. **Required Skill Coverage (15%)**: A gating mechanism. Calculates the percentage of strictly required skills present. If required skills are missing, a heavy non-linear penalty multiplier is applied to the final score to prevent unqualified candidates from ranking high through vague semantic similarity.
4. **Evidence / Coherence (10%)**: Checks *where* the skill is mentioned. Skills found in "Experience" or "Projects" receive a higher score (1.0) than skills merely listed in a "Skills" section (0.5), rewarding concrete evidence over buzzword stuffing.

**Mathematical Formula**:
```
Base Score = (Semantic * 0.40) + (Keyword * 0.35) + (Required * 0.15) + (Coherence * 0.10)
Penalty Multiplier = max(0.40, 1.0 - (Missing_Fraction * 0.6))
Final Score = Base Score * Penalty Multiplier
```

## Setup & Running

### Prerequisites
- Python 3.12+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv pymupdf sentence-transformers rapidfuzz "google-genai" python-multipart pytest reportlab

# Optional: Add your Gemini API Key in backend/.env for AI explanations and Bias detection
# echo "GEMINI_API_KEY=your_key_here" > .env

# Seed the database with demo candidates
python scripts/seed_data.py

# Run the server
uvicorn app.main:app --reload
```
*Backend runs on http://localhost:8000*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on http://localhost:5173*

### 3. Demo Workflow
1. Go to http://localhost:5173
2. Click **Login as Employer**
3. Open the **Full Stack Developer** job.
4. Click **Run Nexora Ranking** to see the AI pipeline in action.
5. Click a candidate to view the deep-dive evidence breakdown and top-3 explanations.
6. Use the floating chat button in the bottom right to ask the AI recruiter why a candidate ranked higher than another.
