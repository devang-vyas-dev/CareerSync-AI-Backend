# CareerSync-AI 🚀

**Transform resumes into ranked internships and personalized learning roadmaps.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.114.0-green.svg)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-2.31.0-orange.svg)](https://supabase.io)
[![Groq](https://img.shields.io/badge/Groq-1.7.0-purple.svg)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/opensource/licenses/MIT)

---

## 📌 Quick Overview

CareerSync-AI is a backend platform that helps students and job seekers:
- **Parse** resumes using AI (Groq Qwen model)
- **Analyze** skill gaps against target roles (SDE, Data Science, AI/ML, Web Dev)
- **Match** against free remote internships (Remotive & Jobicy APIs)
- **Generate** personalized learning roadmaps with resources
- **Store** resumes and progress in Supabase

> **Core Value**: Turn any resume into actionable career guidance — for free.

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| **Framework** | FastAPI (Python) |
| **Database/Auth** | Supabase (PostgreSQL + JWT) |
| **AI/ML** | Groq (Qwen 3.6B 27B), Google Gemini |
| **PDF Parsing** | PyPDF2 |
| **APIs** | Remotive, Jobicy |
| **Env Management** | python-dotenv |
| **CORS** | FastAPI CORSMiddleware |

---

## 📦 Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-org/careersync-ai.git
cd careersync-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your Supabase URL/Key and Groq API Key

# 4. Run the server
uvicorn app.main:app --reload --port 8000
```

> **Required env vars** (in `.env`):
> - `SUPABASE_URL` — Your Supabase project URL
> - `SUPABASE_KEY` — Your Supabase anon/public key
> - `SUPABASE_JWT_SECRET` — Supabase JWT secret
> - `GROQ_API_KEY` — Groq API key for AI parsing
> - `GEMINI_API_KEY` — Google Gemini key for roadmap generation

---

## � API Endpoints

| Method | Endpoint | Description |
|-------|----------|-------------|
| **GET** | `/` | Root — "CareerSync AI Backend is running 🚀" |
| **GET** | `/health` | Health check — status + auth readiness |
| **POST** | `/api/v1/auth/sync` | Sync user profile to Supabase `profiles` table |
| **GET** | `/api/v1/auth/me` | Get current user profile |
| **POST** | `/api/v1/resume/upload` | Upload & parse a resume PDF |
| **GET** | `/api/v1/internships/recommendations` | Get ranked internships matching user skills |
| **GET** | `/api/v1/internships/all` | Fetch all free remote tech internships |
| **POST** | `/api/v1/roadmap/generate` | Generate a personalized learning roadmap |
| **GET** | `/api/v1/roadmaps/my-roadmaps` | Get user's saved roadmaps |

---

## 🧠 How It Works

1. **Upload Resume** → PDF is parsed by Groq AI → skills, education, experience extracted
2. **Skill Gap Analysis** → User's skills compared against target role requirements (SDE, Data Science, AI/ML, Web Dev)
3. **Internship Matching** → Free remote internships ranked by how well user's skills match
4. **Roadmap Generation** → Personalized learning path with YouTube + Docs resources
5. **Progress Tracking** → All data stored in Supabase for persistence

---

## 📊 Example Workflow

```text
Student uploads PDF résumé
         ↓
Groq AI extracts: skills=[Python, SQL], education=[], experience=[]
         ↓
Select target role: "SDE"
         ↓
Gap engine calculates: 40% match → missing: [System Design, APIs, Docker]
         ↓
Ranked internships: Python Developer Intern @ Razorpay (80% match) ✨
         ↓
Roadmap generated: 5 steps → Learn Python → Master SQL → etc.
```

---

## 🚀 Future Process: Adding Payment → Launching as Startup

This section outlines the roadmap from **freemium → paid → startup launch**.

### Phase 1: Payment Integration 💳

| Step | Action | Notes |
|------|--------|-------|
| 1 | **Choose payment provider** — Stripe or Razorpay (India) | Both have Python SDKs & free tiers |
| 2 | **Create pricing plans** — Free (limited roadmaps/internships), Pro (unlimited + priority matching) | Define features per tier |
| 3 | **Add webhook endpoints** — Handle successful payments, subscription updates, cancellations | Secure webhook signing |
| 4 | **Extend user model** — Add `subscription_status`, `plan_type`, `payment_id` fields in Supabase | Migration script |
| 5 | **Protect premium routes** — `roadmap/generate`, `internships/recommendations` check plan tier | Return friendly upgrade prompt |
| 6 | **Add Stripe/Razorpay Checkout** — One-time or monthly recurring payments | Use their hosted checkout for PCI compliance |

### Phase 2: Startup Launch 🚀

| Step | Action | Notes |
|------|--------|------|
| 1 | **Domain & branding** — Custom domain, logo, color scheme | Vercel/Netlify for frontend |
| 2 | **SEO & content marketing** — Blog posts on "How to get an internship", "Roadmaps for SDE roles" | Organic traffic |
| 3 | **Referral program** — Give 1 month Pro for every friend who upgrades | Viral growth loop |
| 4 | **Analytics** — Add PostHog or Google Analytics for funnel tracking | Measure conversion: signup → upload → payment |
| 5 | **Email notifications** — Welcome, roadmap ready, subscription renewal | Resend or SendGrid (free tier) |
| 6 | **Launch on Product Hunt / Indie Hackers** — Early adopter feedback loop | Capture early testimonials |
| 7 | **Iterate based on feedback** — Add skill assessments, mock interviews, company matching | Stay focused on core value |

---

## 📦 Project Structure

```
careersync-ai/
├── app/
│   ├── api/          # FastAPI route modules
│   ├── core/         # Config, auth, supabase client
│   ├── models/       # Pydantic schemas
│   └── services/     # Business logic (gap engine, parser, matcher, roadmap)
├── .env              # Environment variables (gitignored)
├── requirements.txt  # Python dependencies
├── main.py           # App entry point
└── README.md         # You are here! 📖
```

---

## 🛡️ Security Notes

- All Supabase auth uses **ES256 JWT tokens** — verified server-side
- Passwords never stored — handled by Supabase Auth
- CORS restricted to verified frontend origin
- Environment variables loaded from `.env` (never commit to repo!)
- PDF files stored in Supabase Storage with user-owned paths

---

## 🛠️ Development

```bash
# Run with auto-reload (dev mode)
uvicorn app.main:app --reload --port 8000

# Lint
pylint app/

# Type check (optional)
# FastAPI + Pydantic usually self-doc, but mypy can be added
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by the need to connect students with remote internship opportunities
- Groq for fast, affordable AI parsing
- Supabase for instant backend (Auth + DB + Storage)
- Remotive & Jobicy for free job/internship APIs
- All the test users who gave feedback during development