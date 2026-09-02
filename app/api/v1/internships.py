# app/services/ranking.py

import requests
from typing import List
from app.services.gap_engine import calculate_match_score

ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"

def fetch_internships_from_arbeitnow() -> List[dict]:
    """
    Fetches real internships from Arbeitnow API
    Returns: role, organisation, mode, paid/unpaid, url
    """
    try:
        response = requests.get(ARBEITNOW_API, timeout=15)
        response.raise_for_status()
        data = response.json()

        internships = []
        for job in data.get("data", []):
            title = job.get("title", "").lower()

            # Filter only internships
            if "intern" not in title:
                continue

            description = job.get("description", "").lower()

            # Detect Paid / Unpaid
            is_unpaid = any(word in description for word in ["unpaid", "no stipend", "without pay", "volunteer"])

            # Detect Mode
            location = job.get("location", "")
            is_remote = job.get("remote", False)
            if is_remote or "remote" in location.lower() or "remote" in description:
                mode = "Remote"
            elif "hybrid" in description or "hybrid" in location.lower():
                mode = "Hybrid"
            else:
                mode = "On-site"

            # Detect Stipend from description
            stipend = "Paid"
            if is_unpaid:
                stipend = "Unpaid"
            elif "€" in job.get("description", "") or "$" in job.get("description", ""):
                stipend = "Paid (Check description)"

            internships.append({
                "id": job.get("slug"),
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "mode": mode,
                "stipend": stipend,
                "is_paid": not is_unpaid,
                "required_skills": job.get("tags", []),
                "description": job.get("description", "")[:500],
                "url": job.get("url"),
                "created_at": job.get("created_at")
            })

        return internships

    except Exception as e:
        print(f"[Arbeitnow API Error]: {e}")
        return []

def rank_internships(parsed_skills: List[str], limit: int = 4) -> List[dict]:
    """
    Main function you call from your API route.
    Now returns TOP 4 internships by default
    """
    internships = fetch_internships_from_arbeitnow()

    # Fallback if API fails
    if not internships:
        internships = [
            {
                "id": "fallback-1",
                "title": "Backend Intern",
                "company": "CareerSync Demo",
                "location": "Remote",
                "mode": "Remote",
                "stipend": "10k",
                "is_paid": True,
                "required_skills": ["Python", "FastAPI", "SQL"],
                "url": "#",
            }
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
    return ranked[:limit] # This will now return only 4