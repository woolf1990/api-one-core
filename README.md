# FastAPI Test Project - Local Deployable Repo

## What this includes
- FastAPI app with JWT auth (login + refresh)
- CSV upload endpoint with validations and storage (local or S3 if env configured)
- SQLite by default for easy local runs (can be switched to SQL Server via env)
- Tests using pytest
- Dockerfile and docker-compose sample (optional SQL Server container)

## Quick start (local)
1. Create a virtualenv and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create `.env` (or use `.env.example`) and adjust `SQLALCHEMY_DATABASE_URL` if needed.
   For local quick start, default is SQLite at `sqlite:///./test.db`.

3. Initialize DB and demo users:
   ```bash
   python -c "from app.db.connection import init_db; print('DB init done')"
   ```

4. Run app:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open docs at `http://localhost:8000/docs`

## Notes
- For production use a real database (SQL Server/Postgres) and configure AWS S3 credentials if you want to store files on S3.
- The demo creates two users: `uploader`/`password` (role uploader) and `viewer`/`password` (role viewer).
