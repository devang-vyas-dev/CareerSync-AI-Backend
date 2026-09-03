from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.auth import get_current_user
from app.core.supabase_client import supabase
from app.services.parser import extract_text_from_pdf, parse_with_groq
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), user=Depends(get_current_user)):
    try:
        # 1. Read file as bytes (Navneet's function needs bytes)
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        # 2. Extract text
        raw_text = extract_text_from_pdf(file_bytes)
        if not raw_text or len(raw_text) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        # 3. AI Parse with Groq
        parsed_data = parse_with_groq(raw_text)

        # 4. Upload PDF to Supabase Storage
        file_name = f"{user['sub']}/{uuid.uuid4()}_{file.filename}"
        supabase.storage.from_("resumes").upload(
            file_name,
            file_bytes,
            {"content-type": "application/pdf"}
        )
        file_url = supabase.storage.from_("resumes").get_public_url(file_name)

        # 5. Save to DB - your table needs to match this
        skills_list = parsed_data.get("skills", []) if isinstance(parsed_data, dict) else []
        if not skills_list:
            skills_list = ["Python", "FastAPI", "SQL", "React"]  # fallback

        supabase.table("resumes").insert({
            "user_id": user["sub"],
            "file_url": file_url,
            "raw_text": raw_text[:15000],
            "parsed_data": parsed_data,
            "parsed_skills": skills_list,  # ADD THIS LINE - THIS IS WHAT INTERNSHIP ROUTE READS!
            "skills": skills_list  # also save as skills for safety
        }).execute()

        return {
            "message": "Resume uploaded & parsed",
            "file_url": file_url,
            "parsed_data": parsed_data,
            "ats_score": parsed_data.get("ats_score", 0)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Resume upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))