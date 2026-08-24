import requests
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

OLLAMA_HOST = "https://ollama.com"
OLLAMA_MODEL = "gemma4:31b"

EXTRACTION_PROMPT = """You are an expert resume/CV parser used inside an ATS (Applicant Tracking System). Read the ENTIRE raw resume text below from top to bottom — including any header, sidebar, footer, or tabular "Personal Details" / "Bio-data" block — before producing your answer. Do not stop reading after the first few lines.

Personal details (date of birth, gender, marital status, blood group) are very often placed in a short block near the top or bottom of the resume, sometimes laid out as a table or a single line with several colon-separated fields, e.g.:
  "Date of Birth : 12-05-1995   Gender : Male   Marital Status : Single   Blood Group : O+"
They can also appear scattered as separate lines anywhere on the page. Actively search the whole text for these labels (and their common synonyms listed below) instead of assuming they don't exist just because they aren't near the contact info at the top.

Return ONLY a single valid JSON object (no markdown fences, no commentary, no text before or after the JSON) matching EXACTLY this shape:

{
  "first_name": "",
  "last_name": "",
  "metadata": {
    "date_of_birth": "",
    "gender": "",
    "marital_status": "",
    "blood_group": "",
    "location": "",
    "about": "",
    "city": "",
    "state": "",
    "country": "",
    "designation": "",
    "company": "",
    "experience": "",
    "languages": "",
    "skills": []
  },
  "education": [
    {
      "education_level": "",
      "degree_name": "",
      "specialization": "",
      "institution_name": "",
      "university_name": "",
      "start_year": null,
      "end_year": null,
      "percentage": null,
      "cgpa": null
    }
  ],
  "experience": [
    {
      "company_name": "",
      "job_title": "",
      "employment_type": "Full-time",
      "start_date": "",
      "end_date": "",
      "total_experience": "",
      "location": "",
      "description": ""
    }
  ]
}

FIELD-BY-FIELD EXTRACTION GUIDE (use this to decide where to look and how to format each value):
- first_name / last_name: The candidate's full name is usually the largest/boldest text at the very top of the resume, or follows a "Name:" label. Split it into first_name (first token) and last_name (remaining tokens).
- date_of_birth: Look for labels "Date of Birth", "DOB", "D.O.B", "D.O.B.", "Birth Date", "Born on". Convert any date format found (e.g. "12-05-1995", "12/05/1995", "12th May 1995", "1995-05-12") into strict "YYYY-MM-DD". If only a year is given, leave this field empty rather than guessing month/day.
- gender: Look for labels "Gender" or "Sex". Normalize to exactly one of "Male", "Female", or "Prefer not to say". Map abbreviations: "M" -> "Male", "F" -> "Female".
- marital_status: Look for labels "Marital Status" or "Marital Stat". Normalize to exactly "Single" or "Married" (treat "Unmarried" as "Single").
- blood_group: Look for labels "Blood Group", "Blood Grp", or "Blood Type". Normalize to one of "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-" (e.g. "O Positive" -> "O+", "B Neg" -> "B-").
- location / city / state / country: The candidate's own current address/location line (often near the contact details), NOT the address of a school, college, or past employer.
- about: A short professional summary if present, usually under a heading like "Summary", "Objective", "Profile", or "About Me".
- designation / company: The candidate's most recent or current job title and employer — normally the first entry under "Experience"/"Work Experience", or a standalone "Current Role" line.
- experience (top-level array): Only actual paid employment/work history. DO NOT include courses, training programs, internship certificates, or professional certifications here — only real jobs. Internships DO count as experience if held as an employee/intern role.
- metadata.experience: A short string summarizing TOTAL career length, computed by summing the duration of every entry in the "experience" array, formatted like "3 Years 4 Months". If the candidate is a fresher with no work history, use "0 Years 0 Months".
- start_date / end_date (per experience entry): "YYYY-MM" format when known, else an empty string. Leave end_date as "" if the role is current/ongoing (e.g. "Present", "Till date", "Current").
- languages: A single comma-separated string of spoken/written human languages the candidate knows (e.g. "English, Tamil, Hindi"). Do NOT include programming languages here — those belong in "skills".
- skills: A JSON array of individual skill strings (technical and soft skills), each trimmed, deduplicated, and NOT a single comma-separated blob.
- education: One entry per degree/qualification, in any order found in the resume.

Rules:
- You MUST make a best effort to extract personal details — first_name, last_name, date_of_birth, gender, marital_status, location, and blood_group — accurately if they are present anywhere in the resume text, following the guide above.
- If a value genuinely cannot be found anywhere in the resume, keep the field exactly as an empty string (""), empty list ([]), or null. Never use 'N/A', 'Unknown', or invent data that isn't supported by the text.
- Output must be valid JSON only, with no trailing commas and no comments.

Resume text:
---
%s
---
"""


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts raw text from a PDF resume file."""
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    pages_text = [page.extract_text() or "" for page in reader.pages]
    logger.info("Extracted text from PDF: %d pages", len(pages_text))
    return "\n".join(pages_text).strip()


def _clean_json_response(raw: str) -> str:
    """Strips markdown code fences / stray text so the response can be json.loads()'d."""
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return text.strip()


def call_ollama_extract(resume_text: str) -> dict:
    """Sends resume text to the local Ollama model and returns the parsed JSON."""
    prompt = EXTRACTION_PROMPT % resume_text[:12000]

    headers = {"Content-Type": "application/json"}
    api_key = settings.OLLAMA_API_KEY
    if not api_key:
        raise RuntimeError("OLLAMA_API_KEY is not configured. Generate a key at https://ollama.com/settings/keys")
    headers["Authorization"] = f"Bearer {api_key}"

    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        headers=headers,
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise resume-parsing assistant that only replies with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )

    try:
        response.raise_for_status()
    except Exception as e:
        logger.error("Ollama API error: %s - %s", e, response.text)
        raise RuntimeError("Failed to communicate with Ollama API.")

    body = response.json()
    content = body.get("message", {}).get("content", "")
    cleaned = _clean_json_response(content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("Failed to parse Ollama JSON response: %s", content)
        raise RuntimeError("Could not parse resume data returned by the AI model.")


def extract_resume_data(file_path: str) -> dict:
    """Reads a PDF resume and returns structured candidate data via the Ollama model."""
    resume_text = extract_text_from_pdf(file_path)
    if not resume_text:
        raise RuntimeError("Could not read any text from the uploaded resume.")
    return call_ollama_extract(resume_text)
