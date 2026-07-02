# 🤱 MamaGemma: Maternal Health Assistant for Community Midwives

> Built for the **Gemma 4 Good Hackathon** by Kaggle × Google DeepMind · $200,000 Prize Pool

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Model: Gemma 4](https://img.shields.io/badge/Model-Gemma_4-blue.svg)](https://ai.google.dev/gemma)
[![Track: Health & Sciences](https://img.shields.io/badge/Track-Health_%26_Sciences-red.svg)]()

---

## The Problem

In Nigeria, over **30,000 women die annually** from preventable pregnancy complications. Community health workers (CHWs) and midwives operating in primary health centres often face:

- No reliable internet connectivity
- No access to specialist consultation
- Patients who speak limited English
- Overwhelming patient loads with limited support tools

A CHW in a rural Lagos clinic needs to make triage decisions in real time, without being able to "Google it."

## The Solution

**MamaGemma** is an offline-capable AI assistant that supports community midwives during prenatal consultations. It:

- Takes patient vitals, symptoms, and optional photos
- Assesses danger signs using WHO/FMOH guidelines
- Returns a structured clinical recommendation with urgency level
- Summarises findings in **Nigerian Pidgin English** for the patient
- Stores all records **locally**, no data leaves the device

## Why Gemma 4?

| Feature | How MamaGemma uses it |
|---|---|
| **Multimodal input** | Accepts photos of rashes, wounds, medication labels, or ultrasound printouts |
| **On-device / edge deployment** | Gemma 4 E4B runs via Ollama on a local laptop, zero internet required |
| **Function calling** | Structured JSON output for consistent clinical formatting |
| **Apache 2.0 license** | Free to deploy at PHC facilities with no licensing cost |
| **Strong instruction-following** | Reliably follows WHO triage protocols in structured prompts |

## Demo

```
python app.py
# Open http://localhost:5000
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-username/mamagemma.git
cd mamagemma

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key (get free key at aistudio.google.com)
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Run
python app.py

# 5. Open browser
# http://localhost:5000
```

### Offline deployment (via Ollama)
```bash
# Install Ollama: https://ollama.com
ollama pull gemma3:4b    # Edge model — runs on most laptops
# Then set GEMINI_API_KEY="" in .env to use local mode
```

## Tech Stack

- **Model**: Gemma 4 (E4B edge via Ollama for offline; 27B via Google AI Studio for cloud)
- **Backend**: Python / Flask
- **Frontend**: Vanilla HTML/CSS/JS, works in any browser, no install needed
- **Storage**: Local JSON flat file, privacy-first, no cloud sync
- **Languages**: English + Nigerian Pidgin English

## Tracks

- **Primary**: Health & Sciences
- **Secondary**: Digital Equity & Inclusivity (multilingual, offline first)

## Impact

- Target users: ~300,000 community health workers in Nigeria
- Target setting: Primary Health Care centres, rural clinics, mobile outreach
- Languages: English, Pidgin (Yoruba, Hausa, Igbo planned)
- Deployment cost: $0 (runs on existing laptops/tablets)

## Folder Structure

```
mamagemma/
├── app.py              # Flask backend + Gemma 4 integration
├── requirements.txt
├── .env.example
├── static/
│   └── index.html      # Full frontend (single file)
└── data/
    └── consultations.json   # Local consultation log (auto-created)
```

## Safety & Ethics

- MamaGemma is a **decision-support tool**, not a diagnostic device
- All outputs include urgency triage and referral guidance
- No patient data is transmitted to any server
- Danger signs always trigger immediate referral recommendation
- Aligned with Nigerian Federal Ministry of Health maternal care guidelines

## License

Apache 2.0, free to use, modify, and deploy.

---

*Built with ❤️ for the Gemma 4 Good Hackathon.*
