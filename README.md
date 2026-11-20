# job-agent-using-pgvector
# Explainable Job-Matching Agent

An AI-powered backend service that matches PDF resumes to job descriptions using semantic vector search (`pgvector`) and produces structured, evidence-backed LLM rationales. Built for high-signal recruitment and automated career matching.

---

## 🚀 Tech Stack
- **Backend Framework:** Python, FastAPI, SQLAlchemy, Pydantic
- **Database & Vector Search:** PostgreSQL with `pgvector` extension (Dockerized)
- **AI / LLM Integration:** OpenAI API (`text-embedding-3-small`, `gpt-4o-mini` with Structured Outputs)
- **Document Parsing:** `pypdf`

---

## 📊 System Architecture

```text
[PDF Resume] ──► [PyPDF Extractor] ──► [OpenAI Embeddings] ──► [pgvector Query] ──► [FastAPI / Swagger UI]
                                                                     │
                                                                     ▼
                                                         [GPT-4o-mini Structured Rationale]
