from google import genai
from dotenv import load_dotenv
import os, json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_crisis(text):
    prompt = f"""
You are a crisis analysis AI for a hospitality venue.
Analyze this incident and return ONLY raw JSON. No markdown. No explanation.

{{
  "type": "fire/medical/security/structural/other",
  "severity": 0-100,
  "location": "extracted location or unknown",
  "people_affected": estimated number as integer,
  "recommended_responders": ["role1", "role2"]
}}

Incident: "{text}"
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

result = analyze_crisis("Guest collapsed near pool, unconscious, staff panicking")
print(json.dumps(result, indent=2))