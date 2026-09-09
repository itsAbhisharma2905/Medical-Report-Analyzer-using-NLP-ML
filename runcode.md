```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app:app --reload
```

```powershell
streamlit run frontend/streamlit_app.py
```

```powershell
cd frontend-web
npm install
npm run dev
```

```powershell
docker compose up --build
```
