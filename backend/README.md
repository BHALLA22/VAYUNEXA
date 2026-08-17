# VAYUNEXA Backend

FastAPI backend for the VAYUNEXA adaptive wind energy optimization system.

The backend provides APIs for:

- telemetry ingestion and retrieval
- turbine management
- weather data
- energy calculations
- fixed-vs-adaptive comparison
- energy forecasting
- flap-angle optimization
- AI model metrics

## Local setup

From the repository root:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload
