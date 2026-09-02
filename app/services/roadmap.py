import json
from typing import List, Dict
from datetime import datetime, timezone
from app.core.groq_client import get_groq_client
from app.models.schemas import RoadmapStep, RoadmapResponse, RoadmapRequest, TargetRole

def generate_roadmap_service(request: RoadmapRequest, student_id: str) -> RoadmapResponse:
    """
    Uses Groq API (from your.env GROQ_API_KEY) to generate roadmap
    for missing_skills -> returns RoadmapResponse as per Navneet's schema
    """
    client = get_groq_client()

    missing_skills = request.missing_skills
    target_role = request.target_role.value if hasattr(request.target_role, 'value') else str(request.target_role)

    if not missing_skills:
        return RoadmapResponse(
            student_id=student_id,
            target_role=request.target_role,
            roadmap=[],
            total_estimated_days=0,
            generated_at=datetime.now(timezone.utc)
        )

    prompt = f"""
    You are a roadmap generator for career upskilling.

    Target Role: {target_role}
    Missing Skills (user needs to learn): {missing_skills}

    Create a step-by-step roadmap.
    Return ONLY valid JSON array of steps like this:
    {{
      "roadmap": [
        {{
          "step_no": 1,
          "skill": "One skill from {missing_skills}",
          "title": "Short title e.g. Master SQL Basics",
          "description": "What to learn in 2-3 lines",
          "resources": [
            {{"type": "youtube", "title": "SQL Tutorial for Beginners", "url": "https://www.youtube.com/results?search_query=sql+tutorial"}},
            {{"type": "docs", "title": "SQL Official Docs", "url": "https://www.w3schools.com/sql/"}}
          ],
          "estimated_days": 3,
          "is_completed": false
        }}
      ]
    }}

    Rules:
    - One step per missing skill (if 3 missing skills -> 3 steps)
    - step_no starts from 1
    - estimated_days: 2-5 days per skill (beginner friendly)
    - resources: at least 1 youtube + 1 docs/article
    - Order: basics first, then advanced skills
    """

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        data = json.loads(completion.choices[0].message.content)
        steps_data = data.get("roadmap", [])

        roadmap_steps: List[RoadmapStep] = []
        total_days = 0

        for step in steps_data:
            roadmap_steps.append(RoadmapStep(
                step_no=step.get("step_no", len(roadmap_steps)+1),
                skill=step.get("skill", ""),
                title=step.get("title", ""),
                description=step.get("description", ""),
                resources=step.get("resources", []),
                estimated_days=step.get("estimated_days", 3),
                is_completed=False
            ))
            total_days += step.get("estimated_days", 3)

        return RoadmapResponse(
            student_id=student_id,
            target_role=request.target_role,
            roadmap=roadmap_steps,
            total_estimated_days=total_days,
            generated_at=datetime.now(timezone.utc)
        )

    except Exception as e:
        print(f"Groq failed, using fallback: {e}")
        # Fallback if Groq fails
        steps = []
        total = 0
        for i, skill in enumerate(missing_skills):
            days = 3
            total += days
            steps.append(RoadmapStep(
                step_no=i+1,
                skill=skill,
                title=f"Learn {skill} for {target_role}",
                description=f"Master fundamentals and intermediate concepts of {skill} required for {target_role} role.",
                resources=[
                    {"type": "youtube", "title": f"Learn {skill} Full Course", "url": f"https://www.youtube.com/results?search_query=learn+{skill}+for+{target_role}"},
                    {"type": "docs", "title": f"{skill} Documentation", "url": "https://developer.mozilla.org"}
                ],
                estimated_days=days,
                is_completed=False
            ))

        return RoadmapResponse(
            student_id=student_id,
            target_role=request.target_role,
            roadmap=steps,
            total_estimated_days=total,
            generated_at=datetime.now(timezone.utc)
        )