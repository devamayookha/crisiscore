# 🚨 SafeSync

**AI-powered crisis command system for hospitality.**
Staff describe an emergency in plain, even panicked, language. SafeSync classifies it, scores severity, dispatches responders and tracks the response on a live command board.

Built by **Team CrisisCore** for the **Google Solution Challenge 2026**.
Problem statement: *Rapid Crisis Response: Accelerated Emergency Response and Crisis Coordination in Hospitality.*

**🔗 Live demo:** https://crisiscore.onrender.com
*(The free tier may take a short while to wake up on first load.)*

---

## The problem

In a hotel emergency, staff panic. Reports come in broken and unstructured ("smoke everywhere kitchen help fast"), the wrong people get called, and every minute of hesitation adds risk. Most systems assume calm, trained staff filling in structured forms.

## The solution

SafeSync takes the messy report as it is and turns it into action:

```
Plain-text report → Gemini analysis → Classify + Score + Locate
→ Dispatch responders → Action protocol → Live board + Map
```

**No forms. No training. Just describe the crisis.**

---

## Features

- **Natural-language intake:** no dropdowns, works with typos and panic-grammar
- **AI crisis classification:** fire, medical, security, structural or other
- **Severity scoring:** 0–100 with a visual bar and CRITICAL / HIGH / MEDIUM labels
- **Location and people-affected extraction** from free text
- **Dispatched responders:** auto-selected, with Dispatched / En Route / On Site status buttons
- **Immediate Action Protocol:** 5-step SOP for each crisis type
- **AI reasoning:** a one-line explanation of why the severity was assigned
- **Live Command Board:** auto-refreshes every 5 seconds, with a highest-priority incident block and an ACTIVE CRISIS highlight
- **Incident timeline:** timestamped stages (reported, classified, dispatched) in IST
- **Interactive map:** colour-coded pins (red, orange, green) for 70+ Indian cities
- **Fail-safe fallback:** if Gemini is unavailable the app still returns a safe default response and shows a visible fallback notice instead of crashing
- **Persistence:** every incident is stored in MongoDB Atlas with its analysis and timeline

---

## Tech stack

| Layer | Technology |
|---|---|
| AI | Google Gemini API (`gemini-2.5-flash`) via the `google-genai` SDK |
| Backend | Python, Flask, Gunicorn |
| Database | MongoDB Atlas (PyMongo) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Map | Leaflet.js + OpenStreetMap |
| Hosting | Render |

---

## Project structure

```
crisiscore/
├── app.py                # Flask app, Gemini analysis, API routes
├── config/
│   └── db.py             # MongoDB connection
├── templates/
│   └── index.html        # Dashboard (UI, map, command board)
├── requirements.txt
├── runtime.txt           # Python version for Render
├── gunicorn.conf.py
└── .env                  # Local secrets (not committed)
```

---

## API routes

| Method | Route | Description |
|---|---|---|
| GET | `/` | Dashboard |
| POST | `/analyze` | Takes `{ "text": "..." }`, returns the structured analysis and saves the incident |
| GET | `/incidents` | Latest 20 incidents, newest first |
| GET | `/test-gemini` | Health check for the Gemini connection |
| GET | `/test-db` | Health check for the MongoDB connection |

**Example response from `/analyze`:**

```json
{
  "type": "fire",
  "severity": 95,
  "location": "Mumbai",
  "people_affected": 3,
  "recommended_responders": ["fire_department", "paramedics", "security_manager"],
  "reasoning": "Active fire with trapped people and smoke inhalation risk.",
  "saved": true
}
```

---

## Run locally

**Prerequisites:** Python 3.11, a [Gemini API key](https://aistudio.google.com), and a MongoDB Atlas cluster.

```bash
# 1. Clone
git clone https://github.com/devamayookha/crisiscore.git
cd crisiscore

# 2. Create and activate a virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add environment variables (see below)

# 5. Run
python app.py
```

Open http://127.0.0.1:5000

### Environment variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
MONGO_URI=your_mongodb_atlas_connection_string
```

Never commit `.env`. Make sure it is listed in `.gitignore`.

---

## Deployment (Render)

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn --workers 1 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT app:app`
- **Environment variables:** `GEMINI_API_KEY`, `MONGO_URI`, `PYTHON_VERSION=3.11.0`
- In MongoDB Atlas, allow Render's IPs under **Network Access**

---

## How the fail-safe works

The Gemini call is wrapped in error handling. If it fails (quota, network, malformed output), `/analyze` returns a safe default (`severity: 50`, responder: floor manager) with `fallback_used: true`. The UI then shows a red "AI Unavailable, Fallback Logic Activated" notice. The incident is still logged and the response workflow keeps going.

---

## Known limitations

This is a hackathon prototype.

- Gemini free-tier quota is limited; heavy use triggers the fallback
- The map matches the extracted location against a built-in list of ~70 Indian cities, not a full geocoder
- The command board polls every 5 seconds instead of using WebSockets
- Responder status buttons are UI-only and are not persisted or sent to real dispatch services
- No authentication

---

## Roadmap

- Multi-property monitoring for hotel chains
- Integration with real emergency-service and alerting APIs (SMS / WhatsApp)
- Persisted responder status and incident closure
- Multilingual input (Hindi, Tamil, Malayalam and more)
- Voice-based reporting
- Real-time sync and analytics on response times

---

## Team CrisisCore

Built by first-year B.Tech AI & Data Science students.
GitHub: [@devamayookha](https://github.com/devamayookha)
