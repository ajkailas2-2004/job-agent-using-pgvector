import os
from sqlalchemy.orm import Session
from database import SessionLocal, JobPost, engine
from openai import OpenAI

# Initialize OpenAI client (make sure to set your OPENAI_API_KEY environment variable or replace with your key)
# client = OpenAI(api_key="your-openai-api-key-here")

SAMPLE_JOBS = [
    {
        "title": "Software Engineer Intern",
        "company": "Elip",
        "location": "Remote",
        "stipend": "$5,000/mo",
        "is_remote": 1,
        "job_description": "We are looking for a high-signal Software Engineer Intern to build core infrastructure. Responsibilities include building explainable AI matching systems, working with FastAPI, PostgreSQL, pgvector, and LLM evaluations."
    },
    {
        "title": "Backend Engineering Intern",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "stipend": "$4,500/mo",
        "is_remote": 0,
        "job_description": "Join our backend team to develop scalable microservices using Python, FastAPI, Docker, and PostgreSQL. Experience with REST APIs and database optimization required."
    }
]

def get_embedding(text: str):
    # If you have an OpenAI API key, uncomment below:
    # response = client.embeddings.create(input=[text], model="text-embedding-3-small")
    # return response.data[0].embedding
    
    # For testing without an active API key right now, return a dummy 1536-dimensional vector:
    return [0.05] * 1536

def ingest_sample_jobs():
    db: Session = SessionLocal()
    try:
        for job_data in SAMPLE_JOBS:
            # Check if job already exists
            existing = db.query(JobPost).filter_by(title=job_data["title"], company=job_data["company"]).first()
            if existing:
                print(f"Job already exists: {job_data['title']} at {job_data['company']}")
                continue
                
            vector = get_embedding(job_data["job_description"])
            
            job = JobPost(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                stipend=job_data["stipend"],
                is_remote=job_data["is_remote"],
                job_description=job_data["job_description"],
                embedding=vector
            )
            db.add(job)
        db.commit()
        print("Sample jobs successfully ingested into PostgreSQL!")
    except Exception as e:
        db.rollback()
        print(f"Error ingesting jobs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_sample_jobs()