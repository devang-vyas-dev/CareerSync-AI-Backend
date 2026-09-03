import json
import os
from typing import List
from datetime import datetime, timezone
from dotenv import load_dotenv
import google.generativeai as genai

from app.models.schemas import RoadmapStep, RoadmapResponse, RoadmapRequest

load_dotenv()


def generate_roadmap_service(request: RoadmapRequest, student_id: str) -> RoadmapResponse:
    """
    Uses Gemini 2.0 Flash (GEMINI_API_KEY from.env)
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in.env - please add it")

    genai.configure(api_key=api_key)

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
    Missing Skills: {missing_skills}

    Create a step-by-step roadmap.
    Return ONLY valid JSON object with key "roadmap" like this:
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
    - One step per missing skill
    - step_no starts from 1
    - estimated_days: 2-5 days per skill
    - resources: at least 1 youtube + 1 docs/article
    - Order: basics first, then advanced
    - Return ONLY JSON, no markdown, no backticks
    """

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            generation_config={
                "temperature": 0.3,
                "response_mime_type": "application/json"
            }
        )

        response = model.generate_content(prompt)

        # Clean response if it has ```json wrapper
        text = response.text.strip()
        if text.startswith("```"):
            text = text.strip("`").replace("json", "", 1).strip()

        data = json.loads(text)
        steps_data = data.get("roadmap", [])

        roadmap_steps: List[RoadmapStep] = []
        total_days = 0

        for step in steps_data:
            roadmap_steps.append(RoadmapStep(
                step_no=step.get("step_no", len(roadmap_steps) + 1),
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
        print(f"Gemini 2.0 Flash failed, using fallback: {e}")
        steps = []
        total = 0
        for i, skill in enumerate(missing_skills):
            days = 3
            total += days
            steps.append(RoadmapStep(
                step_no=i + 1,
                skill=skill,
                title=f"Learn {skill} for {target_role}",
                description=f"Master fundamentals and intermediate concepts of {skill} required for {target_role} role.",
                resources=[
                    {"type": "youtube", "title": f"Learn {skill} Full Course",
                     "url": f"https://www.youtube.com/results?search_query=learn+{skill}+for+{target_role}"},
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