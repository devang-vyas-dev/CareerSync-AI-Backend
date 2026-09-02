from typing import List, Dict
from app.models.schemas import SkillGap, SkillLevel

ROLE_SKILLS_MAP = {
    "SDE": ["Python", "DSA", "OOPs", "SQL", "Git", "REST APIs", "System Design"],
    "Data Science": ["Python", "SQL", "Pandas", "Machine Learning", "Statistics", "Data Visualization"],
    "AI/ML Engineer": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "NLP", "Groq", "LangChain"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "FastAPI", "PostgreSQL", "Git"],
    "Other": ["Python", "Communication", "Problem Solving"]
}

def get_required_skills(target_role: str, custom_skills: List[str] = None) -> List[str]:
    if custom_skills:
        return custom_skills
    return ROLE_SKILLS_MAP.get(target_role, ROLE_SKILLS_MAP["Other"])

def calculate_match_score(user_skills: List[str], required_skills: List[str]) -> Dict:
    user_map = {s.lower(): s for s in user_skills}
    user_lower_set = set(user_map.keys())

    matched = []
    missing = []
    gaps: List[SkillGap] = []

    for req in required_skills:
        if req.lower() in user_lower_set:
            matched.append(req)
            gaps.append(SkillGap(skill=req, status="matched", level=SkillLevel.INTERMEDIATE))
        else:
            missing.append(req)
            gaps.append(SkillGap(skill=req, status="missing", level=SkillLevel.BEGINNER))

    score = int((len(matched) / len(required_skills) * 100)) if required_skills else 0

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "gaps": gaps
    }
