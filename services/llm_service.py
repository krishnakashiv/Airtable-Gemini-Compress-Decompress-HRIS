import os
import time
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai
import ast

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_service")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2


def build_prompt(applicant_json: dict) -> str:
    """
    Construct the prompt string to send to Gemini based on the applicant JSON.
    """
    return f"""
    You are a recruiting analyst. Given this JSON applicant profile, do four things:
    1. Provide a concise 75-word summary.
    2. Rate overall candidate quality from 1-10 (higher is better).
    3. List any data gaps or inconsistencies you notice.
    4. Suggest up to three follow-up questions to clarify gaps(MUST)

    Return exactly:
    Summary: <text>
    Score: <integer>
    Issues: <comma-separated list or 'None'>
    Follow-Ups: [question1, question2, question3]

    Applicant JSON:
    ```json
    {json.dumps(applicant_json, indent=2)}"""


def analyze_applicant(applicant_json: dict) -> dict:
    prompt = build_prompt(applicant_json)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Sending prompt to Gemini (attempt {attempt})")
            response = model.generate_content(prompt)
            text = response.text.strip()
            return parse_response(text)

        except Exception as e:
            logger.error(f"Gemini API error on attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_BASE ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("Maximum retry attempts reached. Returning fallback values.")
                return {
                    "summary": None,
                    "score": None,
                    "issues": "LLM request failed",
                    "follow_ups": None,
                }


def parse_response(text: str) -> dict:
    summary = extract_field(text, "Summary:")
    score = extract_field(text, "Score:")
    issues = extract_field(text, "Issues:")
    follow_ups = extract_followups(text)

    return {
        "summary": summary,
        "score": int(score) if score and score.isdigit() else None,
        "issues": issues,
        "follow_ups": follow_ups
    }


def extract_field(text: str, label: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith(label):
            return line.split(":", 1)[1].strip()
    return None


def extract_followups(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("Follow-Ups:"):
            raw = line.split(":", 1)[1].strip()

            try:
                parsed = ast.literal_eval(raw)
                if isinstance(parsed, list):
                    return "\n".join(parsed)
            except Exception as e:
                # Fall back to returning raw if parsing fails
                return raw

    return None
