from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os, json
from datetime import datetime
from config.db import get_db

load_dotenv()

app = Flask(__name__)

def analyze_crisis(text):
    import urllib.request
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key={api_key}"
    
    prompt = f"""Analyze this hospitality emergency and return ONLY raw JSON:
{{"type":"fire/medical/security/structural/other","severity":0-100,"location":"extracted or unknown","people_affected":integer,"recommended_responders":["role1","role2"]}}
Incident: "{text}" """

    body = json.dumps({"contents":[{"parts":[{"text":prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"}, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
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
                "analysis": result,
                "timestamp": datetime.utcnow().isoformat()
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

@app.route("/test-db")
def test_db():
    db = get_db()
    if db is not None:
        return jsonify({"status": "connected"})
    return jsonify({"status": "failed"})

if __name__ == "__main__":
    app.run(debug=True)