import json
from typing import List, Dict
from app.core.groq_client import get_groq_client

# Fallback DB if Groq fails
ROLE_SKILLS_DB = {
    "SDE": ["Python", "DSA", "OOPs", "SQL", "Git", "REST APIs", "System Design", "Operating System", "DBMS"],
    "Data Science": ["Python", "SQL", "Pandas", "NumPy", "Machine Learning", "Statistics", "Data Visualization"],
    "AI/ML Engineer": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "NLP", "LangChain", "Groq"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "FastAPI", "PostgreSQL", "Git"],
    "Other": ["Python", "Communication", "Problem Solving", "Git", "SQL"]
}

def get_required_skills(target_role: str, custom_skills: List[str] = None) -> List[str]:
    if custom_skills and len(custom_skills) > 0:
        return custom_skills
    role_str = target_role.value if hasattr(target_role, 'value') else str(target_role)
    return ROLE_SKILLS_DB.get(role_str, ROLE_SKILLS_DB["Other"])

def calculate_match_score(user_skills: List[str], required_skills: List[str]) -> Dict:
    """
    Returns only matched_skills and missing_skills
    Uses GROQ_API_KEY from.env
    """
    client = get_groq_client()

    prompt = f"""
    You are a skill gap analyzer.
    User skills from resume: {user_skills}
    Required skills for role: {required_skills}

    Compare them case-insensitively.
    Return ONLY valid JSON with this exact format:
    {{
      "matched_skills": ["skills user already has"],
      "missing_skills": ["skills user lacks"]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        data = json.loads(completion.choices[0].message.content)

        return {
            "matched_skills": data.get("matched_skills", []),
            "missing_skills": data.get("missing_skills", [])
        }

    except Exception as e:
        print(f"Groq failed, fallback: {e}")
        # Simple fallback
        user_lower = set([s.lower().strip() for s in user_skills])
        matched = [r for r in required_skills if r.lower().strip() in user_lower]
        missing = [r for r in required_skills if r.lower().strip() not in user_lower]

        return {
            "matched_skills": matched,
            "missing_skills": missing
        }