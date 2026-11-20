import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pypdf import PdfReader
from pydantic import BaseModel
from typing import List
from database import SessionLocal, JobPost
from ingest_jobs import get_embedding

app = FastAPI(
    title="Explainable Job-Matching Agent",
    description="Matches resumes to jobs using pgvector and provides explainable fit breakdowns."
)

class JobMatchResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    stipend: str
    similarity_score: float
    explanation: dict

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

def generate_explainable_fit(resume_text: str, job: JobPost, similarity: float) -> dict:
    """
    Generates an explainable breakdown comparing resume text against the job description.
    (Replace with an OpenAI structured-output call once your API key is configured.)
    """
    resume_lower = resume_text.lower()
    jd_lower = job.job_description.lower()
    
    # High-signal technical keywords to inspect
    target_skills = ["python", "fastapi", "postgresql", "pgvector", "docker", "llm", "ai", "sql", "rest", "api"]
    matched_skills = [skill for skill in target_skills if skill in resume_lower and skill in jd_lower]
    missing_skills = [skill for skill in target_skills if skill not in resume_lower and skill in jd_lower]
    
    return {
        "overall_fit": "Strong Match" if similarity >= 0.75 else "Moderate Match",
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "rationale": f"Candidate aligns on {', '.join(matched_skills) if matched_skills else 'core engineering fundamentals'} for the {job.title} role at {job.company}."
    }

@app.post("/match-resume", response_model=List[JobMatchResponse])
async def match_resume(file: UploadFile = File(...), top_k: int = 5):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")
    
    file_bytes = await file.read()
    resume_text = extract_text_from_pdf(file_bytes)
    
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the uploaded PDF.")
    
    # Generate embedding for the resume
    resume_vector = get_embedding(resume_text)
    
    db: Session = SessionLocal()
    try:
        # Query pgvector ordered by cosine distance (<=>)
        distance_expr = JobPost.embedding.cosine_distance(resume_vector)
        results = (
            db.query(JobPost, distance_expr.label("distance"))
            .order_by(distance_expr)
            .limit(top_k)
            .all()
        )
        
        matches = []
        for job, distance in results:
            # Convert cosine distance (0 to 2) into a similarity score (0 to 1)
            similarity = round(max(0.0, 1.0 - float(distance)), 4)
            explanation = generate_explainable_fit(resume_text, job, similarity)
            
            matches.append(
                JobMatchResponse(
                    id=job.id,
                    title=job.title,
                    company=job.company,
                    location=job.location,
                    stipend=job.stipend,
                    similarity_score=similarity,
                    explanation=explanation
                )
            )
        return matches
    finally:
        db.close()