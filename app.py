import os
import json
import base64
import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from google.genai import types
from PIL import Image
import io

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Configure Gemma via AI Studio
# Set GEMINI_API_KEY in your .env or environment
API_KEY = os.environ.get("GEMINI_API_KEY", "")

CONSULTATIONS_FILE = "data/consultations.json"

# ── Danger signs that always trigger urgent referral ──────────────────────────
DANGER_SIGNS = [
    "bleeding", "haemorrhage", "hemorrhage", "fits", "convulsion", "seizure",
    "unconscious", "faint", "severe headache", "blurred vision", "swollen face",
    "no fetal movement", "cord prolapse", "placenta previa", "eclampsia",
    "preeclampsia", "severe pain", "fever above 38", "high bp", "high blood pressure"
]

SYSTEM_PROMPT = """You are MamaGemma, an expert maternal health assistant supporting community midwives and health workers in Nigeria.

Your role is to:
1. Help assess pregnant women during prenatal checkups
2. Identify danger signs that require urgent referral to a hospital
3. Give clear, practical guidance in simple English or Nigerian Pidgin English
4. Follow WHO and Nigerian FMOH maternal health guidelines
5. Always prioritise safety — when in doubt, refer

Response format (always use this JSON structure):
{
  "assessment": "Brief clinical assessment in 2-3 sentences",
  "danger_signs_detected": true or false,
  "urgency_level": "routine" | "watch" | "urgent" | "emergency",
  "recommendations": ["Action 1", "Action 2", "Action 3"],
  "referral_needed": true or false,
  "referral_reason": "Reason if referral needed, else null",
  "pidgin_summary": "A 2-3 sentence summary in Nigerian Pidgin English for the patient",
  "follow_up": "When to return or what to monitor"
}

Urgency levels:
- routine: Normal pregnancy, standard care
- watch: Mild concern, monitor closely
- urgent: Needs hospital visit today
- emergency: Call ambulance / go to hospital immediately

Always be compassionate, practical, and safety-first. Never discourage a midwife from seeking help."""


def load_consultations():
    if os.path.exists(CONSULTATIONS_FILE):
        with open(CONSULTATIONS_FILE, "r") as f:
            return json.load(f)
    return []


def save_consultation(data):
    consultations = load_consultations()
    consultations.append(data)
    os.makedirs("data", exist_ok=True)
    with open(CONSULTATIONS_FILE, "w") as f:
        json.dump(consultations, f, indent=2)


def check_danger_signs_local(text):
    """Quick local check for danger signs without API call."""
    text_lower = text.lower()
    return any(sign in text_lower for sign in DANGER_SIGNS)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/assess", methods=["POST"])
def assess():
    data = request.get_json()

    patient_age = data.get("patient_age", "")
    gestation_weeks = data.get("gestation_weeks", "")
    gravida_para = data.get("gravida_para", "")
    chief_complaint = data.get("chief_complaint", "")
    vitals = data.get("vitals", {})
    symptoms = data.get("symptoms", [])
    notes = data.get("notes", "")
    image_b64 = data.get("image_b64", None)  # optional photo

    # Build clinical summary for the model
    vitals_text = ""
    if vitals:
        parts = []
        if vitals.get("bp"): parts.append(f"BP: {vitals['bp']}")
        if vitals.get("pulse"): parts.append(f"Pulse: {vitals['pulse']} bpm")
        if vitals.get("temp"): parts.append(f"Temp: {vitals['temp']}°C")
        if vitals.get("weight"): parts.append(f"Weight: {vitals['weight']} kg")
        if vitals.get("fundal_height"): parts.append(f"Fundal height: {vitals['fundal_height']} cm")
        vitals_text = ", ".join(parts)

    prompt = f"""Maternal health assessment request:

Patient: {patient_age} years old
Gestation: {gestation_weeks} weeks
Obstetric history: {gravida_para}
Chief complaint: {chief_complaint}
Vitals: {vitals_text if vitals_text else 'Not recorded'}
Symptoms reported: {', '.join(symptoms) if symptoms else 'None specified'}
Additional notes: {notes if notes else 'None'}

Please assess this patient and provide your structured response in the JSON format specified."""

    # Local danger sign pre-check
    full_text = f"{chief_complaint} {' '.join(symptoms)} {notes}".lower()
    local_danger = check_danger_signs_local(full_text)

    if not API_KEY:
        # Demo mode — return realistic mock response
        urgency = "emergency" if local_danger else "routine"
        result = {
            "assessment": "Demo mode: API key not configured. In production this uses Gemma 4 via Google AI Studio.",
            "danger_signs_detected": local_danger,
            "urgency_level": urgency,
            "recommendations": [
                "Configure GEMINI_API_KEY to enable full AI assessment",
                "All vital signs should be recorded at each visit",
                "Ensure tetanus vaccination is up to date"
            ],
            "referral_needed": local_danger,
            "referral_reason": "Danger signs detected locally" if local_danger else None,
            "pidgin_summary": "MamaGemma dey here to help you. E get demo mode — add API key make e work well well.",
            "follow_up": "Return in 4 weeks or sooner if symptoms worsen"
        }
    else:
        try:
            client = genai.Client(api_key=API_KEY)

            content_parts = [prompt]
            if image_b64:
                image_data = base64.b64decode(image_b64)
                image = Image.open(io.BytesIO(image_data))
                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                content_parts.append(
                    types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")
                )

            response = client.models.generate_content(
                model="gemma-4-31b-it",  # swap to gemma-4 model string when released on AI Studio
                contents=content_parts,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
        except Exception as e:
            import traceback; traceback.print_exc(); return jsonify({"error": str(e)}), 500

    # Save consultation log
    consultation = {
        "id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
        "timestamp": datetime.datetime.now().isoformat(),
        "patient_age": patient_age,
        "gestation_weeks": gestation_weeks,
        "gravida_para": gravida_para,
        "chief_complaint": chief_complaint,
        "vitals": vitals,
        "symptoms": symptoms,
        "result": result
    }
    save_consultation(consultation)

    return jsonify(result)


@app.route("/api/consultations", methods=["GET"])
def get_consultations():
    return jsonify(load_consultations())


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "gemma-4", "api_configured": bool(API_KEY)})


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    app.run(debug=True, port=5000)
