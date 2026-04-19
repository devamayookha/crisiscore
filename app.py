from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os, json
from datetime import datetime
from config.db import get_db

load_dotenv()

app = Flask(__name__)

def analyze_crisis(text):
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
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

@app.route("/test-gemini")
def test_gemini():
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents="Say hello in one word"
        )
        return jsonify({"status": "working", "response": response.text})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400
    result = analyze_crisis(data["text"])
    try:
        db = get_db()
        if db is not None:
            incident = {
                "text": data["text"],
                "analysis": result,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            }
            db.incidents.insert_one(incident)
            result["saved"] = True
            print("Incident saved!")
        else:
            result["saved"] = False
            result["db_error"] = "DB is None"
    except Exception as e:
        result["saved"] = False
        result["db_error"] = str(e)
    return jsonify(result)

@app.route("/incidents", methods=["GET"])
def get_incidents():
    try:
        db = get_db()
        if db is not None:
            raw_incidents = list(db.incidents.find({}).sort("_id", -1).limit(20))
            incidents = []
            for inc in raw_incidents:
                inc["_id"] = str(inc["_id"])
                incidents.append(inc)
            return jsonify(incidents)
        return jsonify([])
    except Exception as e:
        print(f"Get incidents error: {e}")
        return jsonify([])

@app.route("/test-db")
def test_db():
    db = get_db()
    if db is not None:
        return jsonify({"status": "connected"})
    return jsonify({"status": "failed"})

if __name__ == "__main__":
    app.run(debug=True)