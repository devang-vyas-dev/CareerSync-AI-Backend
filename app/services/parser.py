from PyPDF2 import PdfReader
import io
import json
from datetime import datetime, timezone
from app.core.groq_client import get_groq_client

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from PDF bytes using PyPDF2
    This is what Devang's /upload route will call
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def parse_with_groq(resume_text: str) -> dict:
    """
    Sends resume text to Groq and gets structured JSON back
    Returns dict that matches ParsedResume + ATS fields
    """
    client = get_groq_client()

    prompt = f"""
    You are an expert ATS resume parser.
    Extract structured data from this resume.
    Return ONLY valid JSON with this exact schema:
    {{
      "full_name": string or null,
      "email": string or null,
      "skills": ["Python", "React", "SQL",...],
      "education": [{{"degree": "", "institution": "", "year": ""}}],
      "experience": [{{"role": "", "company": "", "duration": ""}}],
      "projects": [{{"name": "", "tech_stack": ["..."]}}],
      "ats_score": int between 0 and 100,
      "strengths": ["strong in backend",...],
      "weaknesses": ["missing quantifiable results",...],
      "suggestions": ["add more projects",...]
    }}

    Resume Text (first 8000 chars):
    {resume_text[:8000]}
    """

    completion = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    data = json.loads(completion.choices[0].message.content)

    # Add extra fields needed for DB
    data["raw_text"] = resume_text
    data["parsed_at"] = datetime.now(timezone.utc).isoformat()

    # Ensure skills is always a list
    if "skills" not in data or not isinstance(data["skills"], list):
        data["skills"] = []

    return data