from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pypdf
from docx import Document
import io
from pydantic import BaseModel
from typing import List, Optional
from app.services.matcher import compute_match
from app.services.parser import parse_resume
from app.models.schemas import MatchRequest

app = FastAPI(title="ResumeIQ API", version="2.0")

# Enable CORS so your HTML frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple resume text extractor
def extract_text_from_file(file: UploadFile):
    content = file.file.read()
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        reader = pypdf.PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif filename.endswith('.docx'):
        doc = Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
    elif filename.endswith('.txt'):
        return content.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(400, "Unsupported file type")

@app.post("/api/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    try:
        raw_text = extract_text_from_file(file)
        return {
            "raw_text": raw_text[:15000],  # limit size
            "success": True
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to parse resume: {str(e)}")

@app.post("/api/match/analyze")
async def analyze_match(request: MatchRequest):
    try:
        # Call the real matching service
        match_result = compute_match(request.resume_text, request.jd_text)
        
        # Convert SkillGap objects to dicts for JSON response
        missing_skills_data = []
        for gap in match_result.missing_skills:
            missing_skills_data.append({
                "skill": gap.skill,
                "category": gap.category,
                "importance": gap.importance,
                "courses": gap.courses
            })
        
        return {
            "success": True,
            "data": {
                "overall_score": match_result.overall_score,
                "hard_skill_score": match_result.hard_skill_score,
                "soft_skill_score": match_result.soft_skill_score,
                "tools_score": match_result.tools_score,
                "qualification_score": match_result.qualification_score,
                "experience_score": match_result.experience_score,
                "can_apply": match_result.can_apply,
                "verdict": match_result.verdict,
                "verdict_detail": match_result.verdict_detail,
                "matched_skills": match_result.matched_skills,
                "missing_skills": missing_skills_data,
                "recommendations": match_result.recommendations
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to analyze match: {str(e)}")

# Health check
@app.get("/")
async def root():
    return {"message": "ResumeIQ API is running", "status": "ok"}
