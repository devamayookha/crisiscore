from flask import Flask, request, jsonify, render_template
from google import genai
from dotenv import load_dotenv
from config.db import get_db
import os, json

load_dotenv()

app = Flask(__name__)
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
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        return {
            "type": "unknown",
            "severity": 50,
            "location": "unknown",
            "people_affected": 1,
            "recommended_responders": ["floor_manager"],
            "error": str(e)
        }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    result = analyze_crisis(data["text"])

    db = get_db()
    if db is not None:
        try:
            incident = {
                "text": data["text"],
                "analysis": result
            }
            db.incidents.insert_one(incident)
            result["saved"] = True
        except Exception as e:
            result["saved"] = False
            result["db_error"] = str(e)
    else:
        result["saved"] = False
        result["db_error"] = "Could not connect to MongoDB"

    return jsonify(result)

@app.route("/incidents", methods=["GET"])
def get_incidents():
    try:
        db = get_db()
        if db is not None:
            incidents = list(db.incidents.find({}, {"_id": 0}).sort("_id", -1).limit(20))
            return jsonify(incidents)
        return jsonify([])
    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)