
## Data Challenge for Globant

### 1. Creating the database with the schemas defined in app/models.py
uv run python -m scripts.init_db

### 2. Ingest Historical Data with Validation
uv run python -m scripts.ingest_historical

### 3. Lanzar el API
uv run uvicorn app.main:app --reload --port 8000