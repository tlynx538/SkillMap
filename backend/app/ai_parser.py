import json
import re
from groq import Groq
import os
from typing import Dict, Any

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Use a current, supported model
MODEL_NAME = "llama-3.3-70b-versatile"  # Fallback: "llama-3.1-8b-instant"

def parse_resume_to_skill_graph(raw_text: str) -> Dict[str, Any]:
    prompt = f"""
You are an expert engineer skill extraction tool. Given the following text (resume, project notes, GitHub README, etc.), extract:

1. A list of **technical skills** (languages, frameworks, tools, methodologies, domains). For each skill, assign:
   - depth_score (1–5) using these rules:
       1 = Heard of it, no hands-on
       2 = Followed a tutorial or course exercise
       3 = Used it on a real project with guidance
       4 = Used independently across multiple projects
       5 = Designed, debugged, or taught it in production
   - recency_score (1–5):
       1 = Last used 5+ years ago
       2 = Last used 3–5 years ago
       3 = Last used 1–3 years ago
       4 = Used within last 12 months
       5 = Actively using now
   - evidence: a short snippet (max 10 words) from the text supporting the depth/recency.

2. A list of **edges** – pairs of skills that were used together on a specific project. For each edge, provide:
   - from: skill name (must match exactly the skill name from the list above)
   - to: skill name
   - project_name: short project identifier
   - outcome: a measurable or descriptive outcome (e.g., "reduced latency by 30%", "shipped to production", "wrote postmortem")
   - link: optional URL (if mentioned in text, otherwise empty string)

Return **only** valid JSON in this exact format (no markdown, no extra text):
{{
  "skills": [
    {{ "name": "Python", "depth_score": 4, "recency_score": 5, "evidence": "built data pipelines for 2 years" }},
    ...
  ],
  "edges": [
    {{ "from": "Python", "to": "PostgreSQL", "project_name": "ETL system", "outcome": "reduced load time by 50%", "link": "" }},
    ...
  ]
}}

Text to analyze:
\"\"\"
{raw_text}
\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content.strip()
        # Clean potential markdown code fences
        cleaned = re.sub(r"^```json\s*|\s*```$", "", response_text, flags=re.MULTILINE)
        return json.loads(cleaned)
    except Exception as e:
        print(f"Groq API error with {MODEL_NAME}: {e}")
        # Optionally try fallback model
        if MODEL_NAME == "llama-3.3-70b-versatile":
            print("Trying fallback model: llama-3.1-8b-instant")
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=4096,
                    response_format={"type": "json_object"}
                )
                response_text = response.choices[0].message.content.strip()
                cleaned = re.sub(r"^```json\s*|\s*```$", "", response_text, flags=re.MULTILINE)
                return json.loads(cleaned)
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
        return {"skills": [], "edges": []}