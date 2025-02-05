from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Get database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    abstract = Column(Text)
    authors = Column(String)
    url = Column(String)
    fetch_date = Column(DateTime, default=datetime.utcnow)
    summary = relationship("PaperSummary", back_populates="paper", uselist=False)

class PaperSummary(Base):
    __tablename__ = "paper_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    key_findings = Column(Text)
    methodology = Column(Text)
    implications = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    paper = relationship("Paper", back_populates="summary")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_paper_by_title(db, title):
    return db.query(Paper).filter(Paper.title == title).first()

def save_paper(db, paper_data):
    paper = Paper(**paper_data)
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper

def save_summary(db, paper_id, summary_data):
    summary = PaperSummary(paper_id=paper_id, **summary_data)
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary
