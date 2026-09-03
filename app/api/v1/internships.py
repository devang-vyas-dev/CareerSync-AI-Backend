from fastapi import APIRouter, Query
from app.core.supabase_client import supabase
# IMPORT FROM YOUR ACTUAL FILE - matcher.py
from app.services.matcher import rank_internships, fetch_tech_jobs_free

router = APIRouter(prefix="/internships", tags=["Internships"])

@router.get("/recommendations")
def get_internship_recommendations(limit: int = Query(4)):
    try:
        result = supabase.table("resumes")\
       .select("*")\
       .order("created_at", desc=True)\
       .limit(1)\
       .execute()

        if not result.data:
            parsed_skills = ["Python", "FastAPI", "SQL", "React", "PostgreSQL", "Git"]
        else:
            # Your table has parsed_skills as jsonb
            parsed_skills = result.data[0].get("parsed_skills", [])
            if isinstance(parsed_skills, str):
                import json
                parsed_skills = json.loads(parsed_skills)

        ranked = rank_internships(parsed_skills, limit=limit)

        return {
            "parsed_skills": parsed_skills,
            "count": len(ranked),
            "internships": ranked
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"error": str(e), "internships": []}

@router.get("/all")
def get_all_internships(limit: int = 4):
    try:
        # Use your actual function
        internships = fetch_tech_jobs_free()

        if not internships:
            internships = [
                {"id": "1", "title": "Python Developer Intern", "company": "Razorpay", "location": "Bangalore, India", "mode": "Remote", "stipend": "15k", "is_paid": True, "required_skills": ["Python", "FastAPI", "SQL"], "url": "#", "description": "Python intern"},
                {"id": "2", "title": "React Intern", "company": "Zerodha", "location": "Remote, India", "mode": "Remote", "stipend": "20k", "is_paid": True, "required_skills": ["React", "JavaScript"], "url": "#", "description": "React intern"},
            ]

        # Add match score for demo
        from app.services.gap_engine import calculate_match_score
        dummy_skills = ["Python","FastAPI","SQL","React","PostgreSQL","Git","Groq","LangChain"]
        for intern in internships[:limit]:
            r = calculate_match_score(dummy_skills, intern.get("required_skills",[]))
            intern.update(r)

        return {"count": len(internships[:limit]), "internships": internships[:limit]}
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"error": str(e), "internships": []}
