# BHASA SETU — Medical ISL Bridge (Portable)

Assistive Indian Sign Language translator — MediaPipe Tasks + BiLSTM (60×126, 46 signs, ~77%) + Streamlit + WebRTC + Edge TTS + Auto-speak.

## Quick Start (Windows)

```powershell
# 1. Unzip anywhere (e.g., D:\bhasa_setu)
# 2. Open PowerShell in that folder
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

# 3. Run
py -m streamlit run app/app.py --server.port 8501
# Open http://localhost:8501
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app/app.py --server.port 8501
```

## Why your friend's zip failed
- Used absolute paths (`C:\bhasa_setu`) → now fixed to `Path(__file__).resolve().parents[1]` (relative)
- Missing `models/isl_model.keras` + `hand_landmarker.task` (must be inside zip) — now included
- Missing deps `streamlit-webrtc`, `streamlit-option-menu`, `deep-translator`, `av` → added to `requirements.txt`
- `__pycache__` / `credentials/token.json` bloat/conflict → excluded from portable zip
- Python 3.14 breaks mediapipe → use **Python 3.11/3.12/3.13** (tested 3.13)
- Need to allow camera permission in browser (Chrome/Edge) + use `localhost`, not `file://`

## Structure
```
bhasa_setu/
├── app/app.py (cinematic 3-phase: Splash → Language → Dashboard, integrated camera, auto-TTS, doctor console)
├── models/isl_model.keras + hand_landmarker.task + label_map.json
├── data/patient_phrases.csv (46 signs, EN/HI)
├── script/realtime_predict.py (standalone OpenCV fallback)
└── requirements.txt
```

## Notes
- No separate OpenCV window — camera is inside the app via WebRTC.
- Auto-speak ON by default (toggle in sidebar). Language pill EN|HI switches entire UI + TTS voice.
- If WebRTC blocked: use 📸 Snapshot fallback in left panel.
- First run downloads ~500MB (tensorflow/mediapipe). Keep internet on.


## Language consistency fix
Clinical prompts now use one English source and exactly one translation. Hindi and Odia use deterministic built-in translations; Odia uses the configured Odia voice. This avoids accidental Hindi `_hi` prompt selection and file/location-dependent wording.
