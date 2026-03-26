# ResumeIQ Career Match Engine

## Structure
- `app/` - FastAPI app code
- `index.html` - frontend UI
- `requirements.txt` - dependencies

## Run locally
```bash
cd c:\projects\web_dev\channel-pic\resumeiq
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open frontend in browser:
- `index.html` (or run `python -m http.server 5500` in same folder)

API endpoint:
- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
