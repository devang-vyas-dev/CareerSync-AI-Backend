import requests
from typing import List
from app.services.gap_engine import calculate_match_score

REMOTIVE_API = "https://remotive.com/api/remote-jobs?category=software-dev"
JOBICY_API = "https://jobicy.com/api/v2/remote-jobs?count=50&tag=india"

def fetch_tech_jobs_free() -> List[dict]:
    """Fetch tech internships/jobs - 100% FREE, NO API KEY"""
    all_jobs = []

    # 1. Remotive - Remote tech jobs (free)
    try:
        r = requests.get(REMOTIVE_API, timeout=15)
        for job in r.json().get("jobs", [])[:50]:
            title = job.get("title", "").lower()
            if "intern" in title: # only internships
                all_jobs.append({
                    "id": str(job.get("id")),
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "location": "Remote (India Allowed)",
                    "mode": "Remote",
                    "stipend": "Paid",
                    "is_paid": True,
                    "required_skills": job.get("tags", []),
                    "description": job.get("description", "")[:600],
                    "url": job.get("url"),
                })
    except Exception as e:
        print(f"Remotive error: {e}")

    # 2. Jobicy - India tag jobs (free)
    try:
        r = requests.get(JOBICY_API, timeout=15)
        for job in r.json().get("jobs", []):
            all_jobs.append({
                "id": str(job.get("id")),
                "title": job.get("jobTitle"),
                "company": job.get("companyName"),
                "location": "India / Remote",
                "mode": "Remote",
                "stipend": "Paid",
                "is_paid": True,
                "required_skills": job.get("jobTag", []),
                "description": job.get("jobExcerpt", "")[:600],
                "url": job.get("url"),
            })
    except Exception as e:
        print(f"Jobicy error: {e}")

    return all_jobs

def rank_internships(parsed_skills: List[str], limit: int = 4) -> List[dict]:
    internships = fetch_tech_jobs_free()

    # If both APIs fail, use fallback
    if not internships:
        internships = [
            {"id": "1", "title": "Python Developer Intern", "company": "Razorpay", "location": "Bangalore, India", "mode": "Remote", "stipend": "15k", "is_paid": True, "required_skills": ["Python", "FastAPI", "SQL"], "url": "#", "description": "Python intern"},
            {"id": "2", "title": "React Intern", "company": "Zerodha", "location": "Remote, India", "mode": "Remote", "stipend": "20k", "is_paid": True, "required_skills": ["React", "JavaScript"], "url": "#", "description": "React intern"},
            {"id": "3", "title": "Data Science Intern", "company": "Swiggy", "location": "India", "mode": "Remote", "stipend": "25k", "is_paid": True, "required_skills": ["Python", "ML"], "url": "#", "description": "Data science intern"},
        ]

    ranked = []
    for intern in internships:
        gap = calculate_match_score(parsed_skills, intern.get("required_skills", []))
        ranked.append({
            **intern,
            "match_score": gap.get("match_score", 0),
            "matched_skills": gap.get("matched_skills", []),
            "missing_skills": gap.get("missing_skills", [])
        })

    ranked.sort(key=lambda x: x["match_score"], reverse=True)
    return ranked[:limit]