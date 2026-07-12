
## Data Challenge for Globant

before execute any of these commands, make sure to activate your environment or use `uv run` as a prefix

### 1. Creating the database with the schemas defined in app/models.py
python -m scripts.init_db

### 2. Ingest Historical Data with Validation
python -m scripts.ingest_historical

### 3. Lanzar el API
uvicorn app.main:app --reload --port 8000

### 4. Ejecutar el Backup
python -m scripts.backup

### 5. Restarurar las tablas desde el Backup
python -m scripts.restore --all