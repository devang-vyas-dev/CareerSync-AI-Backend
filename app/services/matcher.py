import re
import requests
from typing import List
from app.services.gap_engine import calculate_match_score

ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"
JOBICY_API = "https://jobicy.com/api/v2/remote-jobs?count=50&tag=india"
REMOTIVE_API = "https://remotive.com/api/remote-jobs?category=software-dev"
MAX_PAGES = 3

INTERN_RE = re.compile(
    r"(?i)\b(werkstudent|werkstudierende|praktikum|praktikant|intern|trainee|apprentice)\b|working student"
)

TECH_TITLE_RE = re.compile(
    r"(?i)\b(software|developer|engineer|engineering|data\s*(scientist|analyst|engineer)?|"
    r"ai|ml|artificial intelligence|machine learning|technical|analyst|frontend|front-end|"
    r"backend|back-end|fullstack|full-stack|python|java|javascript|typescript|react|devops|"
    r"cloud|web|mobile|ios|android|testing|qa|security|research)\b"
)

UNPAID_HINTS = ("unpaid", "no stipend", "without pay", "volunteer", "ehrenamt")
REMOTE_HINTS = ("remote", "home office", "voll remote", "hybrid remote")
HYBRID_HINTS = ("hybrid", "teilweise remote", "hybrid work")

# Arbeitnow tags are broad taxonomy (e.g. "Director/Management"), NOT skills.
# The match only fires on whole words, so short tokens like "go" can't false-match
# inside German words (e.g. "Vorgehen").
TECH_SKILLS = {
    "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
    "react": "React", "react native": "React Native", "node.js": "Node.js",
    "next.js": "Next.js", "vue": "Vue", "angular": "Angular", "java": "Java",
    "spring boot": "Spring Boot", "spring": "Spring", "golang": "Go", "kotlin": "Kotlin",
    "swift": "Swift", "dart": "Dart", "flutter": "Flutter", "android": "Android",
    "ios": "iOS", "sql": "SQL", "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mysql": "MySQL", "mongodb": "MongoDB", "redis": "Redis", "docker": "Docker",
    "kubernetes": "Kubernetes", "k8s": "Kubernetes", "aws": "AWS", "azure": "Azure",
    "gcp": "GCP", "terraform": "Terraform", "cloud computing": "Cloud Computing",
    "linux": "Linux", "bash": "Bash", "shell": "Shell", "git": "Git", "ci/cd": "CI/CD",
    "machine learning": "Machine Learning", "deep learning": "Deep Learning",
    "nlp": "NLP", "llm": "LLMs", "generative ai": "Generative AI",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch", "keras": "Keras",
    "pandas": "Pandas", "numpy": "NumPy", "scikit-learn": "Scikit-Learn",
    "data science": "Data Science", "data analysis": "Data Analysis",
    "data engineering": "Data Engineering", "etl": "ETL", "spark": "Apache Spark",
    "airflow": "Airflow", "statistics": "Statistics", "power bi": "Power BI",
    "tableau": "Tableau", "excel": "Excel", "data visualization": "Data Visualization",
    "html": "HTML", "css": "CSS", "sass": "Sass", "tailwind": "Tailwind CSS",
    "bootstrap": "Bootstrap", "frontend": "Frontend", "front-end": "Frontend",
    "backend": "Backend", "back-end": "Backend", "fullstack": "Full Stack",
    "full stack": "Full Stack", "rest": "REST APIs", "api": "APIs", "graphql": "GraphQL",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
    "web development": "Web Development", "scrapy": "Scrapy", "selenium": "Selenium",
    "oauth": "OAuth", "jwt": "JWT", "system design": "System Design", "dsa": "DSA",
    "oop": "OOPs", "design patterns": "Design Patterns", "devops": "DevOps",
    "automation": "Automation", "testing": "Testing", "unit testing": "Unit Testing",
    "cypress": "Cypress", "pytest": "Pytest", "junit": "JUnit",
    "microservices": "Microservices", "agile": "Agile", "scrum": "Scrum",
    "communication": "Communication", "teamwork": "Teamwork", "analytics": "Analytics",
}


def _is_internship(title: str) -> bool:
    return bool(INTERN_RE.search(title or ""))


def _extract_required_skills(title: str, description: str, tags: List[str]) -> List[str]:
    text = " ".join([
        title or "",
        description or "",
        " ".join(tags or []),
    ]).lower()
    found = set()
    for token, label in TECH_SKILLS.items():
        if re.search(r"\b" + re.escape(token) + r"\b", text):
            found.add(label)
    return sorted(found)


def _arbeitnow_internships() -> List[dict]:
    internships: List[dict] = []
    seen = set()

    for page in range(1, MAX_PAGES + 1):
        try:
            r = requests.get(ARBEITNOW_API, params={"page": page}, timeout=15)
            r.raise_for_status()
            jobs = r.json().get("data", [])
            if not jobs:
                break
        except Exception as e:
            print(f"[Arbeitnow error page={page}]: {e}")
            break

        for job in jobs:
            title = job.get("title") or ""
            slug = job.get("slug") or title
            if not _is_internship(title):
                continue
            if slug in seen:
                continue
            seen.add(slug)

            location = job.get("location") or ""
            description = job.get("description") or ""
            desc_lower = description.lower()
            is_unpaid = any(w in desc_lower for w in UNPAID_HINTS)

            if job.get("remote") or any(w in location.lower() for w in REMOTE_HINTS) or any(w in desc_lower for w in REMOTE_HINTS):
                mode = "Remote"
            elif any(w in desc_lower or w in location.lower() for w in HYBRID_HINTS):
                mode = "Hybrid"
            else:
                mode = "On-site"

            internships.append({
                "id": slug,
                "title": title,
                "company": job.get("company_name"),
                "location": location,
                "mode": mode,
                "stipend": "Unpaid" if is_unpaid else "Paid",
                "is_paid": not is_unpaid,
                "required_skills": _extract_required_skills(title, description, job.get("tags") or []),
                "description": description[:600],
                "url": job.get("url"),
            })

    return internships


def _remotive_internships() -> List[dict]:
    internships: List[dict] = []
    try:
        r = requests.get(REMOTIVE_API, timeout=15)
        r.raise_for_status()
        for job in r.json().get("jobs", []):
            title = job.get("title") or ""
            if not _is_internship(title):
                continue
            tags = job.get("tags") or []
            internships.append({
                "id": str(job.get("id")),
                "title": title,
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location") or "Remote",
                "mode": "Remote",
                "stipend": "Paid",
                "is_paid": True,
                "required_skills": _extract_required_skills(title, job.get("description") or "", tags),
                "description": (job.get("description") or "")[:600],
                "url": job.get("url"),
            })
    except Exception as e:
        print(f"[Remotive error]: {e}")

    return internships


def fetch_tech_jobs_free() -> List[dict]:
    """
    Fetch REAL tech internships - 100% FREE, NO API KEY.

    Primary source: Arbeitnow (the only free source that returns actual
    internships - Werkstudent/Praktikum/Intern/Trainee roles). Remotive is
    consulted as a secondary remote source. Jobicy is intentionally unused:
    it exposes no skills data and its India feed contains no internship roles.
    """
    internships = _arbeitnow_internships()
    internships.extend(_remotive_internships())
    return internships


def rank_internships(parsed_skills: List[str], limit: int = 4) -> List[dict]:
    internships = fetch_tech_jobs_free()
    if not internships:
        return []

    ranked = []
    for intern in internships:
        gap = calculate_match_score(parsed_skills, intern.get("required_skills", []))
        tech_bonus = 1 if TECH_TITLE_RE.search(intern.get("title") or "") else 0
        ranked.append({
            **intern,
            "match_score": gap.get("match_score", 0),
            "matched_skills": gap.get("matched_skills", []),
            "missing_skills": gap.get("missing_skills", []),
            "gaps": gap.get("gaps", []),
            "_tech_bonus": tech_bonus,
        })

    # Prefer internships with more matched skills first, then higher score,
    # then tech-y titles, then roles declaring more skills.
    ranked.sort(
        key=lambda x: (
            len(x["matched_skills"]),
            x["match_score"],
            x["_tech_bonus"],
            len(x.get("required_skills") or []),
        ),
        reverse=True,
    )
    for r in ranked:
        r.pop("_tech_bonus", None)
    return ranked[:limit]
