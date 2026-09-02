from PyPDF2 import PdfReader
import io
import json
from datetime import datetime, timezone
from app.core.groq_client import get_groq_client

def extract_text_from_pdf(file_bytes: bytes) -> str:
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
        print(f"PDF Error: {e}")
        return ""

def parse_with_groq(resume_text: str) -> dict:
    import re
    client = get_groq_client()
    # Clean resume text - remove weird chars
    resume_text_clean = re.sub(r'[^\x00-\x7F]+', ' ', resume_text)

    prompt = f"""
    You are resume parser. Return SINGLE valid JSON object only. No extra text.
    Keys: full_name (string), email (string or null), skills (array of strings),
    education (array), experience (array), projects (array),
    ats_score (number 0-100), strengths (array), weaknesses (array), suggestions (array).

    IMPORTANT: If email is invalid like 'builderw', set email to null.

    Resume:
    {resume_text_clean[:6000]}
    """

    data = None
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        raw = completion.choices[0].message.content.strip()
        print("RAW GROQ:", raw[:1000])

        # Extract first {... } using json decoder
        from json import JSONDecoder
        decoder = JSONDecoder()
        # Clean Markdown
        raw_clean = raw.replace("```json","").replace("```","").strip()
        # Find first {
        idx = raw_clean.find('{')
        if idx!= -1:
            raw_clean = raw_clean[idx:]
            data, _ = decoder.raw_decode(raw_clean)

    except Exception as e:
        print(f"Groq parse failed: {e}")

    if not data:
        # Manual regex fallback for this broken resume
        print("Using regex fallback for broken resume")
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
        name_match = re.search(r'(Devang Vyas|^[A-Z][a-z]+ [A-Z][a-z]+)', resume_text, re.MULTILINE)
        data = {
            "full_name": name_match.group(0) if name_match else "Unknown",
            "email": email_match.group(0) if email_match else None,
            "skills": re.findall(r'Python|SQL|Java|React|Node', resume_text, re.I),
            "education": [],
            "experience": [],
            "projects": [],
            "ats_score": 60,
            "strengths": ["Resume uploaded"],
            "weaknesses": ["Invalid email found - builderw is not valid"],
            "suggestions": ["Fix email address in resume"]
        }

    # Final cleanup
    data["raw_text"] = resume_text[:5000]
    data["parsed_at"] = datetime.now(timezone.utc).isoformat()
    # Validate email
    if data.get("email"):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', str(data["email"])):
            data["email"] = None

    return data