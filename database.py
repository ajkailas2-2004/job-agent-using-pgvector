from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

# Database connection URL for local Docker PostgreSQL
DATABASE_URL = "postgresql://postgres:password@localhost:5432/career_agent"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobPost(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    stipend = Column(String)
    is_remote = Column(Integer)  # 1 for remote, 0 for on-site
    job_description = Column(Text)
    # Using 1536 dimensions for OpenAI text-embedding-3-small
    embedding = Column(Vector(1536))

def init_db():
    # Ensure pgvector extension is created in Postgres
    with engine.connect() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("Database tables and pgvector extension created successfully!")

if __name__ == "__main__":
    init_db()