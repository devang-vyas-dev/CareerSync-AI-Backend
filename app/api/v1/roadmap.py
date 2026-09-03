from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.core.supabase_client import supabase
from app.models.schemas import RoadmapRequest, TargetRole
from app.services.roadmap import generate_roadmap_service

router = APIRouter()

ROLE_SKILLS = {
    "data_scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas"],
    "backend_developer": ["Python", "SQL", "System Design", "APIs", "Docker"],
    "frontend_developer": ["React", "JavaScript", "HTML", "CSS", "TypeScript"],
    "full_stack": ["React", "Node.js", "SQL", "APIs", "Docker"],
    "data_analyst": ["SQL", "Excel", "Python", "Tableau", "Statistics"]
}

@router.post("/generate")
async def create_roadmap(
    target_role: TargetRole,
    resume_id: str = None,
    current_user = Depends(get_current_user)
):
    user_id = current_user.get("sub")

    if resume_id:
        res = supabase.table("resumes").select("*").eq("id", resume_id).execute()
    else:
        res = supabase.table("resumes").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Upload resume first")

    parsed = res.data[0]["parsed_data"] or {}
    resume_skills = [s.lower() for s in parsed.get("skills", [])]

    role_key = target_role.value.lower() if hasattr(target_role, 'value') else str(target_role).lower()
    required = ROLE_SKILLS.get(role_key, ["Python", "SQL", "System Design"])

    missing = [skill for skill in required if skill.lower() not in resume_skills]
    if not missing:
        missing = required[:2]

    roadmap_req = RoadmapRequest(
        target_role=target_role,
        missing_skills=missing
    )

    result = generate_roadmap_service(request=roadmap_req, student_id=user_id)

    supabase.table("roadmaps").insert({
        "user_id": user_id,
        "resume_id": res.data[0]["id"],
        "goal": target_role.value,
        "roadmap_data": result.model_dump(mode='json')
    }).execute()

    return result

@router.get("/my-roadmaps")
async def get_my_roadmaps(current_user = Depends(get_current_user)):
    user_id = current_user.get("id") or current_user.get("user_id") or current_user.get("sub") or current_user.get("userId")
    result = supabase.table("roadmaps").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return result.data