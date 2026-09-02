from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AnalyzeRequest, AnalysisResponse, SkillGap, SkillLevel
from app.core.auth import get_current_user
from app.core.supabase_client import get_supabase_client
from app.services.gap_engine import get_required_skills, calculate_match_score
from app.core.groq_client import get_groq_client
from datetime import datetime, timezone

router = APIRouter()

@router.post("/analyze/{student_id}", response_model=AnalysisResponse)
async def analyze_student(student_id: str, body: AnalyzeRequest, user=Depends(get_current_user)):
    supabase = get_supabase_client()

    # 1. Get latest resume parsed by Devang's upload route
    res = supabase.table("resumes").select("*").eq("student_id", student_id).order("created_at", desc=True).limit(1).execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Resume not found. Upload first via /api/v1/resume/upload")

    parsed = res.data[0].get("parsed_json", {})
    user_skills = parsed.get("skills", [])

    # 2. Get required skills for target role
    required = get_required_skills(body.target_role, body.required_skills)

    # 3. GAP ANALYSIS - Now returns only matched and missing from Groq
    gap_result = calculate_match_score(user_skills, required)
    matched_skills = gap_result.get("matched_skills", [])
    missing_skills = gap_result.get("missing_skills", [])

    # 4. Calculate match_score locally (since gap_engine doesn't return it now)
    match_score = int((len(matched_skills) / len(required) * 100)) if required else 0

    # 5. Build gaps list for schema compatibility (from matched/missing)
    gaps = []
    for skill in matched_skills:
        gaps.append(SkillGap(skill=skill, status="matched", level=SkillLevel.INTERMEDIATE))
    for skill in missing_skills:
        gaps.append(SkillGap(skill=skill, status="missing", level=SkillLevel.BEGINNER))

    # 6. AI Summary via Groq using your.env key
    client = get_groq_client()
    summary_prompt = f"""
    You are a career coach.
    User skills: {user_skills}
    Target Role: {body.target_role.value}
    Matched Skills: {matched_skills}
    Missing Skills (Gap): {missing_skills}

    Write a 2-line motivational, ATS-friendly summary.
    Mention what is strong and what needs to be improved.
    """

    try:
        summary_res = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.5
        )
        summary = summary_res.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq summary failed: {e}")
        summary = f"Good foundation with {', '.join(matched_skills[:3])}. Focus on learning {', '.join(missing_skills[:3])} to become {body.target_role.value} ready."

    # 7. Final Response
    return AnalysisResponse(
        student_id=student_id,
        target_role=body.target_role,
        match_score=match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        gaps=gaps,
        summary=summary,
        analyzed_at=datetime.now(timezone.utc)
    )